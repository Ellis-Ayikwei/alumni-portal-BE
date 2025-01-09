#!/usr/bin/python3
""" objects that handle all default RestFul API actions for Group Members """

from datetime import date
import datetime
from email.policy import strict
from turtle import update
from colorama import Fore
from flask import Flask, jsonify, request, abort
from models import storage
from models.alumni_group import AlumniGroup
from models.contract import Status as CStatus
from models.engine.db_storage import ContractMember
from models.group_member import GroupMember

from api.v1.src.views import app_views
from models.invite import Invite


@app_views.route(
    "/group_members/my_groups_memberships/<user_id>",
    methods=["GET"],
    strict_slashes=False,
)
def get_user_group_memberships(user_id):
    """Retrieve all group memberships for a specific user"""
    group_memberships = storage.all(GroupMember).values()
    user_memberships = []
    for membership in group_memberships:
        membership_info = membership.to_dict()
        membership_info["user_info"] = (
            membership.user_info.to_dict() if membership.user_info else None
        )
        user_memberships.append(membership_info)
    return jsonify(user_memberships), 200


@app_views.route("/group_members", methods=["GET"])
def get_all_group_members():
    """Retrieve all group members"""
    group_members = storage.all(GroupMember).values()
    members_list = []
    for member in group_members:
        member_dict = member.to_dict()
        # member_dict["user_info"] = (
        #     member.user_info.to_dict() if member.user_info else None
        # )
        members_list.append(member_dict)
    return jsonify(members_list), 200


@app_views.route("/group_members/<member_id>", methods=["GET"])
def get_group_member(member_id):
    """Retrieve a specific group member by ID"""
    member = storage.get(GroupMember, member_id)
    if member is None:
        abort(404, description="Group member not found")
    member_dict = member.to_dict()
    member_dict["user_info"] = member.user_info.to_dict()
    member_dict["beneficiaries"] = [
        beneficiary.to_dict() for beneficiary in member.beneficiaries
    ]
    return jsonify(member_dict), 200


@app_views.route(
    "/alumni_groups/<group_id>/members", methods=["GET"], strict_slashes=False
)
def get_members_of_group(group_id):
    """Retrieve all members of a specific group"""
    group = storage.get(AlumniGroup, group_id)
    if group is None:
        abort(404, description="Group not found")
    members = group.members
    members_list = [
        {
            **member.to_dict(),
            "user_info": {
                "id": member.user_info.id,
                "full_name": member.user_info.full_name,
            },
        }
        for member in members
    ]
    return jsonify(members_list), 200


@app_views.route(
    "/alumni_groups/<group_id>/members", methods=["POST"], strict_slashes=False
)
def create_group_member(group_id):
    """
    Create a new group member

    If the request contains an invite code, check if the code is valid and
    has not been used before. If it has, send a 400 response with an error
    message. If it's valid, increment the times used and set the last used
    date to the current datetime.

    If the user is already a member of the group, return a 409 response with
    a message indicating that the user is already a member.

    Otherwise, create a new GroupMember object with the provided data and
    save it to the database.

    Returns a JSON response with the newly created GroupMember object's
    dictionary representation, with a 201 status code.
    """
    group = storage.get(AlumniGroup, group_id)
    if group is None:
        abort(404, description="Group not found")
    if group.current_contract and group.current_contract.status != CStatus.ACTIVE:
        abort(400, description=f"group {group.name}'s Contract is not active")

    if not request.json:
        abort(400, description="Not a JSON")

    data = request.json
    required_fields = ["user_id"]
    for field in required_fields:
        if field not in data:
            abort(400, description=f"Missing {field}")

    # Check if the user is already a member of the group
    all_members = storage.all(GroupMember)
    existing_member = None
    for member in all_members.values():
        if member.user_id == data["user_id"] and member.group_id == group_id:
            existing_member = member
    if existing_member is not None:
        abort(
            409,
            description=f"{existing_member.user_info.username} is already a member of the group",
        )

    if "action" in data and data["action"] == "join":
        # Check if the invite code is valid
        print(data)
        invite = storage.get(Invite, data["invite_id"])
        if invite is None:
            abort(400, description="Invalid Invite code")

        # Check if the invite is valid for this group
        if invite.group_id != group_id:
            abort(400, description="Invite not valid for this group")

        # If the invite has already been used, return an error
        # if invite.times_used >= 1:
        #     abort(400, description="Invite has already been used")

        # if invite.creator_id == data['user_id']:
        #     abort(400, description="Invite code cannot be used by the creator")

        # Increment the times used and set the last used date to the current datetime
        invite.times_used += 1
        invite.last_used_at = datetime.datetime.utcnow()

    # Create new GroupMember object
    new_member = GroupMember(**data, group_id=group_id)

    storage.new(new_member)
    storage.save()

    return jsonify(new_member.to_dict()), 201


@app_views.route("/group_members/<group_id>/check/<member_id>", methods=["GET"])
def check_group_member(group_id, member_id):
    """Retrieve a specific group member by ID"""
    if not request.json:
        abort(400, description="Not a JSON")

    all_members = storage.all(GroupMember)
    existing_member = None
    for member in all_members.values():
        if member.user_id == member_id and member.group_id == group_id:
            existing_member = member
    if existing_member is not None:
        abort(
            409,
            description=f"{existing_member.user_info.username} is already a member of the group",
        )
    return jsonify({"status": "ok"}), 200


@app_views.route("/group_members/<member_id>", methods=["PUT"])
def update_group_member(member_id):
    """Update an existing group member"""
    member = storage.get(GroupMember, member_id)
    group = storage.get(AlumniGroup, member.group_id)

    if member is None:
        abort(404, description="Group member not found")

    if not request.get_json():
        abort(400, description="Not a JSON")

    ignore = ["status", "user_info", "beneficiaries"]
    data = request.get_json()

    for key, value in data.items():
        if key not in ignore:
            print(key)
            setattr(member, key, value)

    if "status" in data:
        if (
            group.current_contract
            and group.current_contract.to_dict()["status"] == "LOCKED"
        ):
            print(group.current_contract.status)
            abort(400, description="Contract is not active")
        if data["status"] == "APPROVED":
            member._approve()
        elif data["status"] == "DISAPPROVED":
            member._disapprove()

    storage.save()
    return jsonify({}), 200


@app_views.route("/group_members/<member_id>", methods=["DELETE"])
def delete_group_member(member_id):
    """Delete a group member"""
    group_member = storage.get(GroupMember, member_id)
    if group_member is None:
        abort(404, description="Group member not found")

    alumni_group = storage.get(AlumniGroup, group_member.group_id)
    if alumni_group is None:
        abort(400, description="Alumni group not found")

    if (
        alumni_group.current_contract
        and alumni_group.current_contract.status != CStatus.ACTIVE
    ):
        abort(400, description="Contract is not active")

    if group_member.is_president:
        group_member.handle_president_removal()

    group_member._remove_from_contract_members()
    storage.delete(group_member)
    storage.save()
    return jsonify({}), 200
