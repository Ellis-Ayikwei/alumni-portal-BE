from functools import wraps
from flask import Flask, g, request, jsonify
from datetime import datetime



def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user') or not g.user:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not g.user.has_role(role_name):
                return jsonify({'error': 'Role required'}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator