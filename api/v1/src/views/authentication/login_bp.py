#!/usr/bin/python3
""" Login the user """
import logging
import flask
from flask import Flask, abort, jsonify, request, make_response

from api.v1.src.views.authentication.logout_bp import AuditStatus
from flask_jwt_extended import (
    create_refresh_token,
    get_csrf_token,
    set_access_cookies,
    set_refresh_cookies,
)
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
import datetime
from flask_limiter import Limiter
from api.v1.src.helpers.helper_functions import get_user_id_from_all_user
from api.v1.src.services.auditslogging.logginFn import log_audit
from api.v1.src.views import app_auth
from models import storage
from models.user import User
from flask import g, jsonify


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app_auth.route("/login", methods=["POST"], strict_slashes=False)
def login() -> tuple[dict, int]:
    """Handle login requests.

    Args:
        data (dict): A dictionary containing the username/email and password.

    Returns:
        tuple: A tuple containing the response data and HTTP status code.
    """
    from api.v1.app import bcrypt, ACCESS_EXPIRES

    data = request.get_json()
    
    

    if (
        not data
        or ("username" not in data and "email" not in data)
        or "password" not in data
    ):
        return jsonify({"message": "Missing username/email or password"}), 400

    user_id: int = None
    user_id = get_user_id_from_all_user(
        username=data.get("username"), email=data.get("email")
    )

    if user_id is None:
        abort(404, description="User not found")

    user: User = storage.get(User, user_id)

    if user and user.verify_password(data["password"]):
        if not user.is_active:
            abort(
                401,
                description="Your Account Is inActive kindly Ask the president to activate it ",
            )
        access_token: str = create_access_token(
            identity=user.id, expires_delta=ACCESS_EXPIRES
        )
        refresh_token: str = create_refresh_token(identity=user.id)

        user_data = user.to_dict()
        user_data.pop("permissions", None) 
        response: flask.Response = make_response(jsonify(user_data))
        # response: flask.Response = make_response(jsonify(user.to_dict()))
        
        response.headers["Authorization"] = "Bearer " + access_token
        response.headers["X-Refresh-Token"] = refresh_token
        # print("response headers", response.headers)
        log_audit(
            user_id, "logged in", status=AuditStatus.COMPLETED, details=None, item_audited=None
        )
        return response, 200
    log_audit(
        user_id, "failed log in", status=AuditStatus.FAILED, details=None, item_audited=None
    )

    return jsonify({"message": "Invalid credentials"}), 401


@app_auth.route("/refresh_token", methods=["POST"])
@jwt_required(refresh=True)
def refresh_access_token() -> tuple[flask.Response, int]:
    """
    Refresh an access token.

    Args:
        None

    Returns:
        tuple: A tuple containing the response data and HTTP status code.
    """
    from api.v1.app import bcrypt, ACCESS_EXPIRES

    user_id: str = get_jwt_identity()
    access_token: str = create_access_token(
        identity=user_id, expires_delta=ACCESS_EXPIRES
    )
    refresh_token: str = create_refresh_token(identity=user_id)

    response: flask.Response = make_response(jsonify({"message": "Token refreshed!"}))
    response.headers["Authorization"] = "Bearer " + access_token
    response.headers["X-Refresh-Token"] = refresh_token

    return response, 200



