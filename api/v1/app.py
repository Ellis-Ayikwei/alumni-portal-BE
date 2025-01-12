import datetime

from math import perm
import os
import sys
from colorama import Fore
from flask import Flask, make_response, jsonify, request
from flask_mail import Mail
import redis
from flask_uploads import configure_uploads, UploadSet, ALL
from pathlib import Path
from dotenv import load_dotenv

from api.v1.src.services.auditslogging.logginFn import (
    log_audit,
    app_views_info_logger,
    app_views_debug_logger,
    app_views_error_logger,
    app_auth_info_logger,
    app_auth_error_logger,
)

from .src.views import app_views, app_auth
from flasgger import Swagger
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from models.user import User
from models import storage

bcrypt = Bcrypt()
mail = Mail()
jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)
load_dotenv()

ACCESS_EXPIRES = datetime.timedelta(hours=1)
uploaded_files = UploadSet("files", ALL)


def create_app():
    app = Flask(__name__)
    jwt = JWTManager(app)

    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["FLASK_MAIL_DEBUG"] = True

    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

    print(os.getenv("MAIL_USERNAME"))
    print(os.getenv("MAIL_PASSWORD"))
    print(app.config["MAIL_USERNAME"])
    print(app.config["MAIL_PASSWORD"])
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")
    mail.init_app(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        jti = jwt_payload["jti"]
        token_in_redis = jwt_redis_blocklist.get(jti)
        return token_in_redis is not None

    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your_default_secret")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    app.config["FIRST_REQUEST"] = True

    app.config["UPLOADED_FILES_DEST"] = "./uploads"

    configure_uploads(app, uploaded_files)

    app.config["CORS_HEADERS"] = ["Content-Type", "Authorization", "X-Refresh-Token"]
    app.config["JWT_SECRET_KEY"] = "super-secret"

    # Initialize extensions
    bcrypt.init_app(app)

    CORS(
        app,
        resources={r"/*": {"origins": ["http://localhost:5173"]}},
        supports_credentials=True,
        expose_headers=["Authorization", "X-Refresh-Token"],
        allow_headers=["Content-Type", "Authorization", "X-Refresh-Token"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    print(app.url_map)

    # Register blueprints
    app.register_blueprint(app_views)
    app.register_blueprint(app_auth)

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers["Access-Control-Allow-Origin"] = request.headers.get(
                "Origin", "*"
            )
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, X-Refresh-Token"
            )
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, DELETE, OPTIONS"
            )
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response, 204

    @app.after_request
    def after_request(response):
        origin = request.headers.get("Origin")
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-Refresh-Token"
        )
        response.headers["Access-Control-Expose-Headers"] = (
            "Authorization, X-Refresh-Token"
        )
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    @app.before_request
    def before_request():
        if request.path == "/alumni/api/v1/auth/logout":
            auth_header = request.headers.get("Authorization")
            if auth_header is None:
                return jsonify({"error": "Unauthorized"}), 401
            print(auth_header)

    # @app.after_request
    # def log_audit_trail(response):
    #     from models.audit_trails import Status
    #     methods_to_audit = ["POST", "PUT", "DELETE"]
    #     success_status_codes = [200, 201, 204]

    #     # Skip logging for non-auditable methods
    #     if request.method not in methods_to_audit:
    #         return response

    #     try:
    #         # Set the action based on the request method
    #         action = request.method

    #         # Parse response data
    #         try:
    #             response_data = json.loads(response.data.decode('utf-8'))
    #         except (ValueError, AttributeError):
    #             response_data = {}

    #         # Parse request data
    #         request_data = json.loads(request.data.decode('utf-8'))

    #         # Determine the user_id from response or request data
    #         user_id = (
    #             response_data.get("id") if "__class__" in response_data and response_data["__class__"] == "User" else
    #             request_data.get("user_id")
    #         )

    #         # Determine the status based on response status code
    #         status =  Status.COMPLETED if response.status_code in success_status_codes else Status.FAILED

    #         # Additional audit details
    #         details = {
    #             "status_code": response.status_code,
    #             "ip_address": request.remote_addr,
    #             "method": request.method,
    #             "url": request.url,
    #         }

    #         # Skip logging if status code is not 204
    #         if response.status_code == 204:
    #             return response

    #         # Item audited
    #         item_audited = response_data.get("id") or response_data.get("name")

    #         # Log the audit
    #         user_name = log_audit(user_id, action, status, details, item_audited=item_audited)

    #         # Log audit trail info
    #         app_views_info_logger.info(f"User: {user_name}, Action: {action}, Status: {status}, Item Audited: {item_audited}")
    #     except Exception as e:
    #         # Log errors
    #         app_views_error_logger.error(f"Failed to log audit trail: {str(e)}")

    #     return response


    from flask import g, request
    from models.user import User
    from flask_jwt_extended import decode_token


    @app.before_request
    def load_user_from_token() -> None:
        """Load the current user into the request context (g)."""

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            g.user = None
            return

        token = auth_header.split("Bearer ")[1]
        try:
            user_id = decode_token(token)["sub"]
            g.user = storage.get(User, user_id)
        except Exception:
            g.user = None


    @app.before_request
    def before_first_request():
        from models.permission import PermissionManager
        from models import storage
        users = storage.all("User").values()
        if app.config.get("FIRST_REQUEST"):
            permissions = storage.all("Permission").values()

            if not permissions:
                # If no permissions exist, set up all permissions
                PermissionManager.setup_all_permissions()

            # Iterate over all users to ensure they have permissions
            for user in users:
                if not user.permissions:
                    PermissionManager.setup_user_permissions(user)

            app.config["FIRST_REQUEST"] = False

    # Configure Swagger
    app.config["SWAGGER"] = {"title": "Alumni Portal Restful API", "uiversion": 3}
    Swagger(app)

    @app.teardown_appcontext
    def close_db(error):
        """Close Storage"""
        storage.close()

    @app.errorhandler(404)
    def not_found(error):
        """404 Error
        ---
        responses:
          404:
            description: a resource was not found
        """
        return make_response(jsonify({"error": "Not found"}), 404)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5004, threaded=True, debug=True)
