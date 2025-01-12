#!/usr/bin/python3
""" objects that handle all default RestFul API actions for Users """
import json
from textwrap import indent

from sqlalchemy import JSON
from api.v1.app import log_audit
from models.permission import Action, Permission, PermissionManager, ResourceType
from models.user import User
from . import app_views
from flask import abort, g, jsonify, make_response, request
from flasgger.utils import swag_from
from models.audit_trails import AuditStatus
from flask_jwt_extended import jwt_required
from api.v1.src.utils.require_permission import require_permission



@app_views.route('/permissions', methods=['GET'])
@jwt_required()
def get_permissions_by_resource():
    """
    Retrieves a dictionary of resource types mapped to their available actions
    """
    from models import storage
    global_user_id = g.user.id
    permissions_by_resource = {}

    # Fetch all permissions
    permissions = storage.all(Permission).values()

    # Iterate over the permissions and group them by resource type
    for permission in permissions:
        resource_type = permission.resource_type.value
        action = permission.to_dict()

        # Initialize the list of actions for the resource type if it doesn't exist
        if resource_type not in permissions_by_resource:
            permissions_by_resource[resource_type] = []

        # Append the action to the corresponding resource type
        permissions_by_resource[resource_type].append(action)

    # Format the response data
    response_data = [
        {
            "resource_type": resource_type,
            "permissions": actions
        }
        for resource_type, actions in permissions_by_resource.items()
    ]

    # Return the response as JSON
    return jsonify(response_data), 200


@app_views.route('/permissions/<user_id>', methods=['PUT'])
@jwt_required()
@require_permission("user", "change")
def update_user_permissions(user_id):
    """
    Update the permissions of a user.
    - Adds permissions to the user.
    - Removes permissions from the user.
    """
    from models import storage
    global_user_id = g.user.id
    log_audit(global_user_id , "updating user permissions", status=AuditStatus.COMPLETED, details=None, item_audited=None)
    from flask import request, jsonify
    from models import storage


    # Fetch the user by ID
    user = storage.get(User, user_id)
    if not user:
        log_audit(global_user_id , "updating user permissions", status=AuditStatus.FAILED, details="User not found", item_audited=user_id)
        return jsonify({"error": "User not found"}), 404

    try:
        # Get the new permissions from the request body
        permissions_ids = request.get_json()
        if not permissions_ids or not isinstance(permissions_ids, list):
            log_audit(global_user_id , "updating user permissions", status=AuditStatus.FAILED, details="Invalid permissions format. Expected a list of IDs.", item_audited=user_id)
            return jsonify({"error": "Invalid permissions format. Expected a list of IDs."}), 400

        # Get current permission IDs
        current_permission_ids = {perm.id for perm in user.permissions}

        # Determine permissions to add and remove
        permissions_to_add = set(permissions_ids) - current_permission_ids
        permissions_to_remove = [perm_id for perm_id in current_permission_ids if perm_id in permissions_ids]
        

        # Add and remove permissions using PermissionManager
        if permissions_to_add:
            permissions_to_add_objs = [storage.get(Permission, perm_id) for perm_id in permissions_to_add]
            PermissionManager.add_permissions_to_user(user, permissions_to_add_objs)

        if permissions_to_remove:
            print("pems to rm/........", permissions_to_remove)
            permissions_to_remove_objs = [storage.get(Permission, perm_id) for perm_id in permissions_to_remove]
            PermissionManager.remove_permissions_from_user(user, permissions_to_remove_objs)

        # Return updated user data
        return jsonify(user.to_dict()), 204
    except Exception as e:
        log_audit(global_user_id , "updating user permissions", status=AuditStatus.FAILED, details=str(e), item_audited=user_id)
        return jsonify({"error": str(e)}), 500



@app_views.route("/users", methods=["GET"], strict_slashes=False)

# @require_permission("user", "view")
def get_users():
    """
    Retrieves the list of all User objects
    """
    from models import storage
    all_users = storage.all(User).values()
    list_users = []
    for user in all_users:
        list_users.append(user.to_dict())
    return jsonify(list_users)


@app_views.route("/users/<user_id>", methods=["GET"], strict_slashes=False)
@require_permission("user", "view")
def get_user(user_id):
    """Retrieves a specific User"""
    from models import storage
    global_user_id = g.user.id
    log_audit(global_user_id , "retrieving user", status=AuditStatus.COMPLETED, details=None, item_audited=user_id)
    from api.v1.src.helpers.helper_functions import get_user_id_from_all_user

    if user_id is None:
        print("no user id entered user the helper function")
        user_id = get_user_id_from_all_user()

    user = storage.get(User, user_id)
    if not user:
        log_audit(global_user_id , "retrieving user", status=AuditStatus.FAILED, details="User not found", item_audited=user_id)
        abort(404)

    return jsonify(user.to_dict())


@app_views.route("/users/<user_id>", methods=["DELETE"], strict_slashes=False)
@jwt_required()
@require_permission("user", "delete")
def delete_user(user_id):
    """
    Deletes a User Object
    """
    from models import storage
    global_user_id = g.user.id
    log_audit(global_user_id , "deleting user", status=AuditStatus.COMPLETED, details=None, item_audited=user_id)

    user = storage.get(User, user_id)
    users = storage.all(User)
    users_dicts = [user.to_dict() for user in users.values()]

    if not user:
        log_audit(global_user_id , "deleting user", status=AuditStatus.FAILED, details="User not found", item_audited=user_id)
        abort(404)

    storage.delete(user)
    storage.save()

    return make_response(jsonify(users_dicts), 200)


@app_views.route("/users", methods=["POST"], strict_slashes=False)
@jwt_required()
@require_permission("user", "add")
# @swag_from('documentation/user/post_user.yml', methods=['POST'])
def post_user():
    """
    Creates a User
    """
    global_user_id = g.user.id
    log_audit(global_user_id , "creating user", status=AuditStatus.COMPLETED, details=None, item_audited=None)
    from api.v1.src.helpers.helper_functions import (
        is_username_already_taken,
        is_email_already_registered,
    )

    data = request.get_json()
    if not data:
        log_audit(global_user_id , "creating user", status=AuditStatus.FAILED, details="Not a JSON", item_audited=None)
        abort(400, description="Not a JSON")
    if "username" not in data or not isinstance(data["username"], str):
        log_audit(global_user_id , "creating user", status=AuditStatus.FAILED, details="Invalid or missing username", item_audited=None)
        abort(400, description="Invalid or missing username")

    if is_username_already_taken(data):
        log_audit(global_user_id , "creating user", status=AuditStatus.FAILED, details="Username already taken. Please choose another one.", item_audited=None)
        abort(
            400, description="Sorry, username already taken. Please choose another one."
        )
    if is_email_already_registered(data):
        log_audit(global_user_id , "creating user", status=AuditStatus.FAILED, details="Email has been registered. Please use another one.", item_audited=None)
        abort(
            400, description="Sorry, email has been registered. Please use another one."
        )
    if "password" not in data or not isinstance(data["password"], str):
        log_audit(global_user_id , "creating user", status=AuditStatus.FAILED, details="Invalid or missing password", item_audited=None)
        abort(400, description="Invalid or missing password")

    new_user = User(**data)
    new_user.save()

    # # Logging user creation attempt
    # if new_user.id:
    #     logging.info(f"User created successfully with id: {new_user.id}")
    # else:
    #     logging.error("Failed to create user")

    return make_response(jsonify(new_user.to_dict()), 201)


@app_views.route("/users/<user_id>", methods=["PUT"], strict_slashes=False)
@jwt_required()
@require_permission("user", "change")
# @swag_from('documentation/user/put_user.yml', methods=['PUT'])
def update_user(user_id: str) -> tuple:
    """
    Updates a User
    """
    from models import storage
    global_user_id = g.user.id
    log_audit(global_user_id , "updating user", status=AuditStatus.COMPLETED, details=None, item_audited=user_id)
    data = request.get_json()
    if not data:
        log_audit(global_user_id , "updating user", status=AuditStatus.FAILED, details="Not a JSON", item_audited=user_id)
        abort(400, description="Not a JSON")

    # new_user_id = get_user_id_from_all_user(username=data.get('username'), email=data.get('email'))
    user = storage.get(User, user_id)
    if not user:
        log_audit(global_user_id , "updating user", status=AuditStatus.FAILED, details="User not found", item_audited=user_id)
        abort(404)
        
    role = data.get("role")
    if role:
        user.role = role
        user.save()
        return make_response(jsonify(user.to_dict()), 200)

    ignore = ["id", "created_at", "updated_at", "__class__"]

    for key, value in data.items():
        if key not in ignore:
            setattr(user, key, value)

    storage.save()
    return make_response(jsonify(user.to_dict()), 204)

@app_views.route(
    "/users/reset_password/<user_id>", methods=["PUT"], strict_slashes=False
)
@jwt_required()
def reset_user_password(user_id: str) -> tuple:
    """Resets a user's password"""
    from models import storage
    global_user_id = g.user.id
    log_audit(global_user_id, "resetting user password", status=AuditStatus.INITIATED, details=None, item_audited=user_id)
    user = storage.get(User, user_id)
    if not user:
        log_audit(global_user_id, "resetting user password", status=AuditStatus.FAILED, details="User not found", item_audited=user_id)
        abort(404)

    data = request.get_json()
    if not data:
        log_audit(global_user_id, "resetting user password", status=AuditStatus.FAILED, details="Not a JSON", item_audited=user_id)
        abort(400, description="Not a JSON")

    current_password = data.get("currentPassword")
    new_password = data.get("newPassword")

    if not current_password or not new_password:
        log_audit(global_user_id, "resetting user password", status=AuditStatus.FAILED, details="Missing current or new password", item_audited=user_id)
        abort(400, description="Missing current password or new password")

    if not user.verify_password(current_password):
        log_audit(global_user_id, "resetting user password", status=AuditStatus.FAILED, details="Invalid current password", item_audited=user_id)
        abort(403, description="Invalid current_password")

    if current_password == new_password:
        log_audit(global_user_id, "resetting user password", status=AuditStatus.FAILED, details="New password same as old password", item_audited=user_id)
        abort(400, description="new password cannot be the same as the old password")

    user.reset_password(current_password, new_password)

    role = data.get("role")
    if role:
        user.role = role

    user.save()
    log_audit(global_user_id, "resetting user password", status=AuditStatus.COMPLETED, details=None, item_audited=user_id)

    return make_response(jsonify(user.to_dict()), 200)

@app_views.route("/users/my_profile/<user_id>", methods=["GET"], strict_slashes=False)
@jwt_required()
def get_user_profile(user_id: str) -> tuple:
    """
    Retrieves a user's profile information
    """
    from models import storage
    
    global_user_id = g.user.id
    user_instance = storage.get(User, user_id)
    if user_instance is None:
        abort(404)

    return make_response(jsonify(user_instance.to_dict()), 200)


@app_views.route(
    "/users/user_profile_completion/<user_id>", methods=["GET"], strict_slashes=False
)
@jwt_required()
def get_user_profile_completion(user_id: str) -> tuple:
    """Calculate the completion percentage of a user's profile."""
    from models import storage
    
    global_user_id = g.user.id
    user_instance = storage.get(User, user_id)
    if user_instance is None:
        abort(404)

    required_fields = [
        "first_name",
        "last_name",
        "email",
        "phone",
        "middle_names",
        "gender",
        "dob",
        "occupation",
        "address",
        "other_names",
    ]

    completed_fields = [
        field for field in required_fields if getattr(user_instance, field)
    ]

    completion_percentage = int((len(completed_fields) / len(required_fields)) * 100)

    return jsonify({"completion_percentage": completion_percentage})



