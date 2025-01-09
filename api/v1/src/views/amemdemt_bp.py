#!/usr/bin/python3
""" objects that handle all default RestFul API actions for Amendments """

import datetime
import stat
from flask import Flask, jsonify, request, abort
from models import storage
from models.amendment import Amendment, AmendmentStatus

from api.v1.src.views import app_views


@app_views.route("/amendments", methods=["GET"])
def get_all_amendments():
    """Retrieve all amendments"""
    amendments = storage.all(Amendment).values()
    amendments_list = [amendment.to_dict() for amendment in amendments]
    return jsonify(amendments_list), 200


@app_views.route("/amendments/<amendment_id>", methods=["GET"])
def get_amendment(amendment_id):
    """Retrieve a specific amendment by ID"""
    amendment = storage.get(Amendment, amendment_id)
    if amendment is None:
        abort(404, description="Amendment not found")
    return jsonify(amendment.to_dict()), 200


@app_views.route("/amendments", methods=["POST"])
def create_amendment():
    """Create a new amendment"""
    if not request.json:
        abort(400, description="Not a JSON")

    data = request.json
    required_fields = ["id", "new_values", "old_values", "status", "amender_user_id"]
    for field in required_fields:
        if field not in data:
            abort(400, description=f"Missing {field}")

    # Create new Amendment object
    new_amendment = Amendment(
        name=data["name"],
        contract_id=data["id"],
        amender_user_id=data["amender_user_id"],
        new_values=data["new_values"],
        old_values=data["old_values"],
        change_date=data.get("change_date", datetime.datetime.utcnow()),
    )

    storage.new(new_amendment)
    storage.save()

    return jsonify(new_amendment.to_dict()), 201


@app_views.route("/amendments/<amendment_id>", methods=["PUT"])
def update_amendment(amendment_id):
    """Update an existing amendment"""
    amendment = storage.get(Amendment, amendment_id)
    if amendment is None:
        abort(404, description="Amendment not found")

    if not request.get_json():
        abort(400, description="Not a JSON")

    data = request.get_json()
    if data["status"] == "APPROVED":
        amendment.approve_amendment(data["user_id"])

    if data["status"] == "REJECTED":
        amendment.disapprove_amendment(data["user_id"])

    storage.save()
    return jsonify(amendment.to_dict()), 200


@app_views.route("/amendments/<amendment_id>", methods=["DELETE"])
def delete_amendment(amendment_id):
    """Delete an amendment"""
    amendment = storage.get(Amendment, amendment_id)
    if amendment is None:
        abort(404, description="Amendment not found")

    storage.delete(amendment)
    storage.save()
    return jsonify({}), 200
