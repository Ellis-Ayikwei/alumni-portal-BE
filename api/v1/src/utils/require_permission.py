
# Permission decorator for API routes
from functools import wraps
from colorama import Fore
from flask import g, jsonify
from functools import wraps
from cachetools import cached, TTLCache


class RequirePermission:
    def __init__(self, resource_type, action, role=None):
        self.resource_type = resource_type
        self.action = action
        self.role = role
        self.cache = TTLCache(maxsize=100, ttl=3600)

    def __call__(self, f):
        from models.user import UserRole
        from flask import abort
        from models.permission import PermissionManager

        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Cache the permission check result
            @cached(self.cache)
            def check_permission(user):
                return PermissionManager.check_permission(user, self.resource_type, self.action)

            if not hasattr(g, 'user') or not g.user:
                print(f"{Fore.BLUE}- Auth Error")
                abort(401, description='Authentication required')

            if self.role and g.user.role != UserRole(self.role):
                print(f"{Fore.BLUE}- User role not allowed ")
                abort(403, description='Permission denied')

            if not check_permission(g.user):
                print(f"{Fore.BLUE}- permission check error {Fore.RESET}")
                abort(403, description='Permission denied')

            return f(*args, **kwargs)
        return decorated_function

require_permission = RequirePermission
