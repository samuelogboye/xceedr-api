from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from flask import current_app, request, jsonify
from functools import wraps
from volumx.models.user import User
from datetime import datetime, timedelta


# Decorator to check if the user is logged in
def login_required(f):
    """
    Decorator function to enforce login requirement for a given function.

    Parameters:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function.

    Raises:
        Exception: If the authorization header is missing or the token is invalid.

    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or not user.is_active:
                return jsonify({'message': 'Unauthorized access'}), 401
        except Exception as e:
            return jsonify({'message': 'Invalid token'}), 401

        return f(user, *args, **kwargs)

    return decorated_function

# Decorator to check if the user is an admin
def admin_required(f):
    """
    Decorator function to enforce login requirement for a given function.

    Parameters:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function.

    Raises:
        Exception: If the authorization header is missing or the token is invalid.

    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or not user.is_active or not user.is_admin:
                return jsonify({'message': 'Unauthorized access'}), 401
        except Exception as e:
            return jsonify({'message': 'Invalid token'}), 401

        return f(user, *args, **kwargs)

    return decorated_function

# Function to check if a user is active
def is_active(user_id):
    user = User.query.get(user_id)
    if not user:
        return False
    return user.is_active
