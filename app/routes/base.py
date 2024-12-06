# app/routes/base.py
from flask import Blueprint, request, jsonify
from app.models.user import User
from functools import wraps
import jwt
from config import Config

base_bp = Blueprint('base', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode token
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            current_user = User.get_by_id(data['user_id'])
            
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

@base_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        'id': current_user['id'],
        'username': current_user['username'],
        'email': current_user['email'],
        'created_at': current_user['created_at'].isoformat() if current_user['created_at'] else None
    }), 200

@base_bp.route('/users', methods=['GET'])
# @token_required
def get_users(current_user):
    users = User.get_all_users()
    return jsonify([{
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'created_at': user['created_at'].isoformat() if user['created_at'] else None
    } for user in users]), 200