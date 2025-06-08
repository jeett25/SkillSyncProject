from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user import User
from app import db

auth_bp = Blueprint('auth', __name__)
user_model = User(db)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check if user already exists
        if user_model.find_by_email(data['email']):
            return jsonify({'error': 'User already exists'}), 400
        
        # Set role (defaults to 'user' if not specified)
        # For admin registration, pass role: 'admin' in the request
        if 'role' not in data:
            data['role'] = 'user'
        
        # Create new user
        user_model.create_user(data)
        return jsonify({
            'message': 'User registered successfully',
            'role': data['role']
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/register/admin', methods=['POST'])
def register_admin():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check if user already exists
        if user_model.find_by_email(data['email']):
            return jsonify({'error': 'User already exists'}), 400
        
        # Force admin role
        data['role'] = 'admin'
        
        # Create admin user
        user_model.create_user(data)
        return jsonify({
            'message': 'Admin user registered successfully',
            'role': 'admin'
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Admin registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])  # Fixed: was @auth.route, now @auth_bp.route
def login():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email
        user = user_model.find_by_email(data['email'])
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user is active
        if not user.get('is_active', True):
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Verify password
        if not user_model.check_password(user['password'], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Update last login
        user_model.update_last_login(str(user['_id']))
        
        # Create JWT token
        access_token = create_access_token(
            identity=str(user['_id']),
            additional_claims={
                'email': user['email'],
                'role': user.get('role', 'user')
            }
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'role': user.get('role', 'user')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    # For JWT, logout is typically handled on client side
    # You could implement token blacklisting here if needed
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    try:
        from flask_jwt_extended import jwt_required, get_jwt_identity
        
        @jwt_required()
        def protected_profile():
            user_id = get_jwt_identity()
            user = user_model.find_by_id(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify({
                'user': {
                    'id': str(user['_id']),
                    'email': user['email'],
                    'role': user.get('role', 'user'),
                    'created_at': user.get('created_at').isoformat() if user.get('created_at') else None,
                    'last_login': user.get('last_login').isoformat() if user.get('last_login') else None,
                    'is_active': user.get('is_active', True)
                }
            }), 200
        
        return protected_profile()
        
    except Exception as e:
        return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500