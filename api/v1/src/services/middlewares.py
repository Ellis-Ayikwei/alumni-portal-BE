#!usr/bin/python3

from functools import wraps
from os import abort
from flask import request, jsonify
from models.user import User
from models import storage


def require_permissions(allowed_roles):
    """Decorator to check if a user has the required permissions."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id")
            user = storage.get(User, user_id)

            if user is None:
                return jsonify({"message": "User not found"}), 404

            if "all" not in allowed_roles and user.role not in allowed_roles:
                return (
                    jsonify({"message": "You are not allowed to perform this action"}),
                    403,
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


@require_permissions("admin", ["user", "admin"])
def _test_decorator():
    print("hello world")


_test_decorator()
