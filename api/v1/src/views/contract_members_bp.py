#!/usr/bin/python3
""" objects that handle all default RestFul API actions for Contract Members """

from flask import Flask, jsonify, request, abort
from models import storage
from models.contract_member import ContractMember
from api.v1.src.views import app_views


@app_views.route("/contract_members", methods=["GET"])
def get_all_contract_members():
    """Retrieve all contract members"""
    contract_members = storage.all(ContractMember).values()
    contract_members_list = [member.to_dict() for member in contract_members]
    return jsonify(contract_members_list), 200


@app_views.route("/contract_members/<member_id>", methods=["GET"])
def get_contract_member(member_id):
    """Retrieve a specific contract member by ID"""
    contract_member = storage.get(ContractMember, member_id)
    if contract_member is None:
        abort(404, description="Contract member not found")
    return jsonify(contract_member.to_dict()), 200


@app_views.route("/contract_members", methods=["POST"])
def create_contract_member():
    """Create a new contract member"""
    if not request.json:
        abort(400, description="Not a JSON")

    data = request.json
    required_fields = ["contract_id", "group_member_id"]
    for field in required_fields:
        if field not in data:
            abort(400, description=f"Missing {field}")

    # Create new ContractMember object
    new_member = ContractMember(
        contract_id=data["contract_id"],
        group_member_id=data["group_member_id"],
        is_amended=data.get("is_amended", False),
    )

    storage.new(new_member)
    storage.save()

    return jsonify(new_member.to_dict()), 201


@app_views.route("/contract_members/<member_id>", methods=["PUT"])
def update_contract_member(member_id):
    """Update an existing contract member"""
    contract_member = storage.get(ContractMember, member_id)
    if contract_member is None:
        abort(404, description="Contract member not found")

    if not request.json:
        abort(400, description="Not a JSON")

    data = request.json
    contract_member.contract_id = data.get("contract_id", contract_member.contract_id)
    contract_member.group_member_id = data.get(
        "group_member_id", contract_member.group_member_id
    )
    contract_member.is_amended = data.get("is_amended", contract_member.is_amended)

    storage.save()
    return jsonify(contract_member.to_dict()), 200


@app_views.route("/contract_members/<member_id>", methods=["DELETE"])
def delete_contract_member(member_id):
    """Delete a contract member"""
    contract_member = storage.get(ContractMember, member_id)
    if contract_member is None:
        abort(404, description="Contract member not found")

    storage.delete(contract_member)
    storage.save()
    return jsonify({}), 200
