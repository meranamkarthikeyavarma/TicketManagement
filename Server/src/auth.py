from flask import Blueprint, request, jsonify
from auth_db import auth_db
import bcrypt
from validators import SignupSchema, LoginSchema
from pydantic import ValidationError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        # Validate input
        data = SignupSchema(**request.json)
        
        # Check if email already exists
        existing_user = auth_db.get_user_by_email(data.email)
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            }), 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(
            data.password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Create user
        user = auth_db.create_user(data.name, data.email, hashed_password)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Failed to create user'
            }), 500
        
        # Remove password from response
        user_without_password = {k: v for k, v in user.items() if k != 'password'}
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'user': user_without_password
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': e.errors()[0]['msg']
        }), 422
    except Exception as e:
        print(f"Signup error: {e}") 
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        # Validate input
        data = LoginSchema(**request.json)
        
        # Find user by email
        user = auth_db.get_user_by_email(data.email)
        if not user:
            return jsonify({
                'success': False,
                'message': 'No user found with this email'
            }), 400
        
        # Verify password
        is_valid_password = bcrypt.checkpw(
            data.password.encode('utf-8'),
            user['password'].encode('utf-8')
        )
        
        if not is_valid_password:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
        
        # Remove password from response
        user_without_password = {k: v for k, v in user.items() if k != 'password'}
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user_without_password
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': e.errors()[0]['msg']
        }), 422
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@auth_bp.route('/users', methods=['GET'])
def get_all_users():
    try:
        users = auth_db.get_all_users()
        # Remove passwords from all users
        users_without_passwords = [
            {k: v for k, v in user.items() if k != 'password'}
            for user in users
        ]
        return jsonify({
            'success': True,
            'users': users_without_passwords
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500