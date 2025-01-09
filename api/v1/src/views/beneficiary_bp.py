#!/usr/bin/python3
""" objects that handle all default RestFul API actions for beneficiaries """


from flask import Flask, jsonify, request, abort
from models import storage
from models.beneficiary import Beneficiary

from api.v1.src.views import app_views
from models.user import User


@app_views.route("/beneficiaries", methods=["GET"])
def get_all_beneficiaries():
    """Retrieve all beneficiaries"""
    beneficiaries = storage.all(Beneficiary).values()
    beneficiaries_list = [beneficiary.to_dict() for beneficiary in beneficiaries]
    return jsonify(beneficiaries_list), 200


@app_views.route("/beneficiaries/<beneficiary_id>", methods=["GET"])
def get_beneficiary(beneficiary_id):
    """Retrieve a specific beneficiary by ID"""
    beneficiary = storage.get(Beneficiary, beneficiary_id)
    if beneficiary is None:
        abort(404, description="Beneficiary not found")
    return jsonify(beneficiary.to_dict()), 200


# @app_views.route('/users/<user_id>/beneficiaries', methods=['GET'])
# def get_user_beneficiaries(user_id):
#     """Retrieve all beneficiaries for a specific user by ID"""
#     user = storage.get(User, user_id)
#     if user is None:
#         abort(404, description="User not found")

#     beneficiaries = user.beneficiaries
#     beneficiaries_list = [beneficiary.to_dict() for beneficiary in beneficiaries]
#     return jsonify(beneficiaries_list), 200


# @app_views.route('/users/<user_id>/beneficiaries', methods=['GET'])
# def get_user_beneficiaries(user_id):
#     """Retrieve all beneficiaries for a specific user by ID"""
#     user = storage.get(User, user_id)
#     if user is None:
#         abort(404, description="User not found")

#     beneficiaries_list = []
#     for beneficiary in user.beneficiaries:
#         print(type(beneficiary))
#         ben_dict = beneficiary.to_dict()
#         print(type(ben_dict))
#         ben_dict['user_info'] = user.to_dict()
#         print("type of user id", type(user))
#         beneficiaries_list.append(ben_dict)


#     return jsonify(beneficiaries_list), 200
@app_views.route("/users/<user_id>/beneficiaries", methods=["GET"])
def get_user_beneficiaries(user_id):
    """Retrieve all beneficiaries for a specific user by ID"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="User not found")

    beneficiaries_list = [beneficiary.to_dict() for beneficiary in user.beneficiaries]
    return jsonify(beneficiaries_list), 200


@app_views.route("/beneficiaries", methods=["POST"])
def create_beneficiary():
    """Create a new beneficiary"""
    if not request.json:
        abort(400, description="Not a JSON")

    data = request.json
    required_fields = [
        "first_name",
        "last_name",
        "email",
        "phone",
        "address",
        "other_names",
        "date_of_birth",
        "relationship_type",
    ]
    for field in required_fields:
        if field not in data:
            abort(400, description=f"Missing {field}")

    new_beneficiary = Beneficiary(**data)
    new_beneficiary.save()

    return jsonify(new_beneficiary.to_dict()), 201


@app_views.route("/beneficiaries/<beneficiary_id>", methods=["PUT"])
def update_beneficiary(beneficiary_id):
    """Update an existing beneficiary"""
    beneficiary = storage.get(Beneficiary, beneficiary_id)
    if beneficiary is None:
        abort(404, description="Beneficiary not found")

    if not request.json:
        abort(400, description="Not a JSON")

    data = request.json
    beneficiary.first_name = data.get("first_name", beneficiary.first_name)
    beneficiary.last_name = data.get("last_name", beneficiary.last_name)
    beneficiary.date_of_birth = data.get("date_of_birth", beneficiary.date_of_birth)
    beneficiary.relationship_type = data.get(
        "relationship_type", beneficiary.relationship_type
    )

    storage.save()
    return jsonify(beneficiary.to_dict()), 200


@app_views.route("/beneficiaries/<beneficiary_id>", methods=["DELETE"])
def delete_beneficiary(beneficiary_id):
    """Delete a beneficiary"""
    beneficiary = storage.get(Beneficiary, beneficiary_id)
    if beneficiary is None:
        abort(404, description="Beneficiary not found")

    storage.delete(beneficiary)
    storage.save()
    return jsonify({}), 200
