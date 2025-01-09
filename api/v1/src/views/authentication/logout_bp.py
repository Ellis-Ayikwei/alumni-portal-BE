#!/usr/bin/python3
""" Logout the user """
from venv import logger
import flask
from flask import g, make_response, jsonify, request
from api.v1.app import log_audit
from flask_jwt_extended import get_jwt, jwt_required
import redis
from api.v1.src.views import app_auth
from models.audit_trails import AuditStatus


@app_auth.route("/logout", methods=["POST"], strict_slashes=False)
@jwt_required()
def logout() -> tuple[dict, int]:
    """
    Logout the user by revoking their access token.
    Rovokes the access token in the Redis cache and returns a success message.


    Returns:
        A JSON response indicating the success or failure of the logout operation.
    """
    from api.v1.app import ACCESS_EXPIRES, jwt_redis_blocklist

    user_id = g.user.id
    try:
        jwt_token = get_jwt()
        jwt_id = jwt_token["jti"]

        jwt_redis_blocklist.set(jwt_id, "", ex=ACCESS_EXPIRES)
        
        log_audit(
                    user_id, "logged out", status=AuditStatus.COMPLETED, details=None, item_audited=None
                )


        return jsonify(message="Access token successfully revoked"), 202

    except Exception as error:
        logger.error(f"Logout error: {error}")
        log_audit(
                    user_id, "logout failed", status=AuditStatus.FAILED, details=None, item_audited=None
                )
        return jsonify(message="Error: Token not found or invalid"), 400
