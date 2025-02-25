#!/usr/bin/python3
""" Register a new user """
from hmac import new
from flask import Blueprint, abort, flash, jsonify, request
from api.v1.src.helpers.helper_functions import (
    is_email_already_registered,
    is_username_already_taken,
)
from .user_validation import validate_user_data
from models.user import User
from api.v1.src.views import app_auth


@app_auth.route("/register", methods=["POST"], strict_slashes=False)
def register() -> tuple[dict, int]:
    """Register a new user
        - check if user already exists
        - check if email is already registered
        - check if username is already taken
        - create new user
    Returns:
        tuple: A tuple containing the response data and HTTP status code

    Args:
        form_data (dict): A dictionary containing the user details

    Returns:
        tuple: A tuple containing the response data and HTTP status code
    """
    print("Registering a new user", flush=True)
    from models.permission import PermissionManager
    form_data = request.get_json()
    print(form_data, flush=True)
    if not form_data:
        abort(400, description="Not a JSON")

    try:
        validated_data = validate_user_data(form_data)
    except ValueError as e:
        abort(400, description=str(e))

    if is_username_already_taken(validated_data["username"]):
        abort(
            400, description="Sorry, username already taken. Please choose another one."
        )

    if is_email_already_registered(validated_data["email"]):
        abort(400, description="Sorry, email already registered. Please log in.")

    new_user = User(**validated_data)
    new_user.save()
    
    if new_user is None:
        abort(500, description="Failed to create user")
    PermissionManager.setup_user_permissions(new_user)

    
    flash("You have registered successfully. Please log in.", "success")
    return jsonify(new_user.to_dict()), 201
