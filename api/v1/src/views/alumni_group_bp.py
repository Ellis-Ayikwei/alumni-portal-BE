#!/usr/bin/python3

"""views for the alumni group blueprint"""

import json
from pydoc import describe
from click import group
from colorama import Fore
from flask import Flask, g, jsonify, request, abort
from models.alumni_group import AlumniGroup, Status
from api.v1.src.services.auditslogging.logginFn import log_audit
from models.audit_trails import AuditStatus
from flask_jwt_extended import get_jwt, jwt_required

from api.v1.src.views import app_views
from models.invite import Invite
from models.user import GroupMember, User
from api.v1.src.utils.require_permission import require_permission


@app_views.route(
    "/alumni_groups/<group_id>/invite_code", methods=["POST"], strict_slashes=False
)
def generate_group_invite(group_id):
    """Generate an invite code for a user to join a specific group"""
    global_user_id = g.user.id
    if not request.get_json():
        abort(400, description="Not a JSON")

    data = request.get_json()
    user_id = data.get("user_id")
    user = storage.get(User, user_id)
    if user is None:
        log_audit(global_user_id, "generate invite code", status=AuditStatus.FAILED, details="User not found", item_audited=None)
        abort(404, description="User not found")

    invite = (
        storage.get_session()
        .query(Invite)
        .filter_by(group_id=group_id, creator_id=user_id)
        .first()
    )

    if not invite:
        invite = Invite(group_id=group_id, creator_id=user_id)
        invite.save()

    log_audit(global_user_id, "generate invite code", status=AuditStatus.COMPLETED, details=None, item_audited=invite.id)
    return jsonify(invite.to_dict()), 200


@app_views.route("/alumni_groups/my_groups/<user_id>", methods=["GET"])
@jwt_required()
def get_user_alumni_groups(user_id):
    """Retrieve all alumni groups a user is a part of"""
    from models import storage
    
    global_user_id = g.user.id
    user = storage.get(User, user_id)
    if user is None:
        log_audit(global_user_id, "get user alumni groups", status=AuditStatus.FAILED, details="User not found", item_audited=None)
        abort(404, description="User not found")

    memberships = [
        {"group_id": membership.group_id} for membership in user.group_memberships
    ]
    memberships_list = []
    for membership in memberships:
        group = storage.get(AlumniGroup, membership["group_id"])
        group_dict = group.to_dict()
        group_dict["members"] = [member.to_dict() for member in group.members]
        if group.president:
            group_dict["president"] = {
                key: value
                for key, value in group.president.to_dict().items()
                if key not in ["groups_as_president", "group_memberships"]
            }
        memberships_list.append(group_dict)
    log_audit(global_user_id, "get user alumni groups", status=AuditStatus.COMPLETED, details=None, item_audited=user_id)
    return jsonify(memberships_list), 200


@app_views.route("/alumni_groups", methods=["GET"])
@jwt_required()
def get_all_alumni_groups():
    """Retrieve all alumni groups"""
    from models import storage


    global_user_id = g.user.id
    alumni_groups = storage.all(AlumniGroup).values()
    alumni_groups_list = []
    for group in alumni_groups:
        group_dict = group.to_dict()
        group_dict["members"] = (
            [member.to_dict() for member in group.members] if group.members else None
        )
        group_dict["insurance_package"] = (
            group.insurance_package.to_dict() if group.insurance_package else None
        )
        alumni_groups_list.append(group_dict)
    return jsonify(alumni_groups_list), 200


@app_views.route("/alumni_groups/<group_id>", methods=["GET"])
@jwt_required()
def get_alumni_group(group_id):
    """Retrieve a specific alumni group by ID"""
    from models import storage

    global_user_id = g.user.id
    alumni_group = storage.get(AlumniGroup, group_id)
    if alumni_group is None:
        log_audit(global_user_id, "get alumni group", status=AuditStatus.FAILED, details="Alumni group not found", item_audited=None)
        abort(404, description="Alumni group not found")
    group_dict = alumni_group.to_dict()
    group_dict["members"] = (
        [member.to_dict() for member in alumni_group.members]
        if alumni_group.members
        else None
    )
    group_dict["insurance_package"] = (
        alumni_group.insurance_package.to_dict()
        if alumni_group.insurance_package
        else None
    )
    group_dict["president"] = (
        alumni_group.president.to_dict() if alumni_group.president else None
    )
    log_audit(global_user_id, "get alumni group", status=AuditStatus.COMPLETED, details=None, item_audited=group_id)
    return jsonify(group_dict), 200


@app_views.route("/alumni_groups", methods=["POST"])
@jwt_required()
# @require_permission("alumni_group", "add")
def create_alumni_group():
    """Create a new alumni group"""
    global_user_id = g.user.id
    if not request.json:
        log_audit(global_user_id, "create alumni group", status=AuditStatus.FAILED, details="Not a JSON", item_audited=None)
        abort(400, description="Not a JSON")

    data = request.json
    required_fields = ["name", "start_date", "end_date"]
    for field in required_fields:
        if field not in data:
            log_audit(global_user_id, "create alumni group", status=AuditStatus.FAILED, details=f"Missing {field}", item_audited=None)
            abort(400, description=f"Missing {field}")

    new_group = AlumniGroup(**data)
    new_group.save()
    log_audit(global_user_id, "create alumni group", status=AuditStatus.COMPLETED, details=None, item_audited=new_group.id)
    return jsonify(new_group.to_dict()), 201


@app_views.route("/alumni_groups/<group_id>", methods=["PUT"])
@jwt_required()
def update_alumni_group(group_id):
    """Update an existing alumni group"""
    from models import storage
    global_user_id = g.user.id
    group = storage.get(AlumniGroup, group_id)
    all_group_members = storage.all(GroupMember).values()

    if group is None:
        log_audit(global_user_id, "update alumni group", status=AuditStatus.FAILED, details="Alumni group not found", item_audited=None)
        abort(404, description="Alumni group not found")

    if not request.get_json():
        log_audit(global_user_id, "update alumni group", status=AuditStatus.FAILED, details="Not a JSON", item_audited=None)
        abort(400, description="Not a JSON")

    group_data = request.get_json()
    group_members = list(filter(lambda x: x.group_id == group_id, all_group_members))

    updateable_fields = [
        "status",
        "name",
        "start_date",
        "end_date",
        "president_user_id",
        "package_id",
        "description",
    ]
    for key, value in group_data.items():
        if key in updateable_fields:
            setattr(group, key, value)
        group.save()

    if "is_president" in group_data and group_data["is_president"]:
        grp_membership = storage.get(GroupMember, group_data["id"])
        for member in group_members:
            member.is_president = False
        group.president_user_id = group_data["president_user_id"]
        grp_membership.is_president = True

    if "status" in group_data and group_data["status"] in Status.__members__:
        group.status = Status[group_data["status"]]

    storage.save()
    log_audit(global_user_id, "update alumni group", status=AuditStatus.COMPLETED, details=None, item_audited=group.id)
    return jsonify(group.to_dict()), 200


@app_views.route("/alumni_groups/<group_id>", methods=["DELETE"])
@jwt_required()
def delete_alumni_group(group_id):
    """Delete an alumni group"""
    from models import storage    

    global_user_id = g.user.id
    alumni_group = storage.get(AlumniGroup, group_id)
    if alumni_group is None:
        log_audit(global_user_id, "delete alumni group", status=AuditStatus.FAILED, details="Alumni group not found", item_audited=None)
        abort(404, description="Alumni group not found")

    storage.delete(alumni_group)
    storage.save()
    log_audit(global_user_id, "delete alumni group", status=AuditStatus.COMPLETED, details=None, item_audited=group_id)
    return jsonify({}), 200


@app_views.route("/alumni_groups/<group_id>/admins/<user_id>", methods=["POST", "DELETE"])
@jwt_required()
def manage_admin(group_id, user_id):
    """Manage admins of an alumni group"""
    from models import storage
    
    global_user_id = g.user.id
    group = storage.get(AlumniGroup, group_id)
    if group is None:
        log_audit(global_user_id, "manage admin", status=AuditStatus.FAILED, details="Alumni group not found", item_audited=None)
        abort(404, description="Alumni group not found")

    if request.method == "POST":
        try:
            group.make_admin(user_id)
            log_audit(global_user_id, "make admin", status=AuditStatus.COMPLETED, details=None, item_audited=user_id)
        except ValueError as e:
            log_audit(global_user_id, "make admin", status=AuditStatus.FAILED, details=str(e), item_audited=user_id)
            abort(400, description=e)
            
    elif request.method == "DELETE":
        try:
            group.remove_admin(user_id)
            log_audit(global_user_id, "remove admin", status=AuditStatus.COMPLETED, details=None, item_audited=user_id)
        except ValueError as e:
            log_audit(global_user_id, "remove admin", status=AuditStatus.FAILED, details=str(e), item_audited=user_id)
            abort(400, description=e)

    return jsonify({}), 200

