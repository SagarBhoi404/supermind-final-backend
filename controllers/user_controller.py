from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime
from models.user_model import connect_to_astra, create_users_table, insert_user, get_user_by_email, get_user_by_id, update_user
from services.user_service import hash_password, generate_jwt_token, decode_jwt_token

user_bp = Blueprint('user', __name__)

# Register user
@user_bp.route('/api/users/register', methods=['POST'])
def register_user():
    data = request.json
    name = data['name']
    email = data['email']
    password = hash_password(data['password'])
    role = data['role']
    created_at = updated_at = datetime.now()

    session = connect_to_astra()
    create_users_table(session)

    user_id = uuid.uuid4()
    insert_user(session, user_id, name, email, password, role, created_at, updated_at)

    return jsonify({'message': 'User registered successfully'}), 201

# Login user and return JWT token
@user_bp.route('/api/users/login', methods=['POST'])
def login_user():
    data = request.json
    email = data['email']
    password = hash_password(data['password'])

    session = connect_to_astra()
    user = get_user_by_email(session, email)

    if user and user.password == password:
        # Generate JWT token
        token = generate_jwt_token(user.user_id, user.email, user.role)
        return jsonify({'message': 'Login successful', 'token': token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# Get user profile (verify JWT token)
@user_bp.route('/api/users/profile', methods=['GET'])
def get_user_profile():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    # Remove the 'Bearer ' prefix from the token if present
    token = token.replace('Bearer ', '')

    # Decode the token and verify it
    payload = decode_jwt_token(token)

    if not payload:
        return jsonify({'message': 'Invalid or expired token'}), 401

    user_id = payload['user_id']
    session = connect_to_astra()
    user = get_user_by_id(session, user_id)

    if user:
        return jsonify({
            'user_id': str(user.user_id),
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        }), 200
    else:
        return jsonify({'message': 'User not found'}), 404

# Update user profile
@user_bp.route('/api/users/profile', methods=['PUT'])
def update_user_profile():
    data = request.json
    user_id = data['user_id']
    name = data.get('name')
    email = data.get('email')
    role = data.get('role')
    updated_at = datetime.now()

    session = connect_to_astra()
    user = get_user_by_id(session, user_id)

    if user:
        update_user(session, user_id, name, email, role, updated_at)
        return jsonify({'message': 'User profile updated successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

# Logout user
@user_bp.route('/api/users/logout', methods=['POST'])
def logout_user():
    return jsonify({'message': 'User logged out successfully'}), 200
