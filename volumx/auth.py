from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
#from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from . import db
from volumx.models.user import User
from functools import wraps
from datetime import datetime, timedelta
from random import randint
from .auth_utils import login_required, admin_required
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, decode_token, get_jwt_identity, get_jwt

# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# Endpoint for user registration
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    # Check if required fields are present in the request data
    if 'email' not in data or 'password' not in data or 'first_name' not in data or 'last_name' not in data:
        return jsonify({'message': 'Incomplete registration data'}), 400

    # turn email to lowercase
    data['email'] = data['email'].lower()

    # Use Regex to Check if the email is valid
    import re

    def is_valid_email(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    if not is_valid_email(data['email']):
        return jsonify({'message': 'Invalid email'}), 400


    try:
        # Check if the username is already taken
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'message': 'Email already exists'}), 400

        # Create a new user
        new_user = User(email=data['email'], first_name=data['first_name'], last_name=data['last_name'], password=generate_password_hash(data['password']))
        new_user.insert()

        access_token = create_access_token(identity=new_user.id, expires_delta=timedelta(hours=1))   # Access token expires in 1 hour
        refresh_token = create_refresh_token(identity=new_user.id, expires_delta=timedelta(days=90))  # Refresh token expires in 24 hours

        # get user data
        userData = {
            "id": new_user.id,
            "email": new_user.email,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email_confirmed": new_user.email_confirmed,
            "profile_picture": new_user.profile_picture,
            "is_active": new_user.is_active,
            "is_admin": new_user.is_admin,
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "createdAt": new_user.createdAt,
            "updatedAt": new_user.updatedAt
        }
        return jsonify({'message': 'User registered successfully.', 'userData': userData}), 201
    except Exception as e:
        current_app.log_exception(exc_info=e)
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "message": "It's not you it's us",
                    "status": False,
                }
            ),
            500,
        )

# Endpoint to confirm the OTP sent to the email
@auth_bp.route('/confirm_otp', methods=['POST'])
def confirm_otp():
    data = request.json

    if 'email' not in data or 'otp' not in data:
        return jsonify({'message': 'Incomplete data'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    otp = str(data['otp'])

    if not user.otp or user.otp != otp:
        return jsonify({'message': 'Invalid OTP'}), 400

    if datetime.now() > user.otp_expiry:
        return jsonify({'message': 'OTP expired'}), 400

    # OTP matches and is within the expiry time, confirm the email
    user.email_confirmed = True
    user.update()
    return jsonify({'message': 'Email confirmed successfully'}), 200


# Endpoint for user login and token generation
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    # Check if required fields are present in the request data
    if 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Email and password are required'}), 400

    # turn email to lowercase
    data['email'] = data['email'].lower()

    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401

    # Generate and return an authentication token for the user
    access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))   # Access token expires in 1 hour
    refresh_token = create_refresh_token(identity=user.id, expires_delta=timedelta(days=90))  # Refresh token expires in 24 hours

    # get user data
    userData = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email_confirmed": user.email_confirmed,
        "profile_picture": user.profile_picture,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "createdAt": user.createdAt,
        "updatedAt": user.updatedAt
        }
    return jsonify({'userData': userData, 'message': 'Logged in successfully'}), 200

# Endpoint for token refresh
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id, expires_delta=timedelta(hours=1))
    return jsonify(access_token=new_access_token, message='Token refreshed successfully', user_data=User.query.get(current_user_id).format()), 200


# Endpoint for user logout
@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logged out successfully'}), 200


# Endpoint for user profile deletion
@auth_bp.route('/profile', methods=['DELETE'])
@admin_required
def delete_profile(user):
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Profile deleted successfully'}), 200

# Endpoint to get all users
@auth_bp.route('/users', methods=['GET'])
#@admin_required
def get_users():
    users = User.query.all()
    total = len(users)
    return jsonify([user.format() for user in users], "total_users:", total), 200

# Endpoint to get a user by ID
@auth_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(user.format()), 200

# Endpoint to update a user by ID
@auth_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    data = request.json
    if 'email' in data:
        user.email = data['email']
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'username' in data:
        user.username = data['username']
    if 'password' in data:
        user.password = generate_password_hash(data['password'])
    db.session.commit()
    return jsonify(user.format()), 200

# Endpoint to delete a user by ID
@auth_bp.route('/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200


# Endpoint to make a user an admin
@auth_bp.route('/users/<user_id>/admin', methods=['PATCH'])
@login_required
def make_admin(user, user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.is_admin = True
    db.session.commit()
    return jsonify(user.format()), 200