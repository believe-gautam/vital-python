from functools import wraps
from flask import request, jsonify
import jwt
import os
from app.models.user import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Invalid token format!'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode token
            data = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=["HS256"])
            current_user = User.get_by_id(data['user_id'])
            
            if not current_user:
                return jsonify({'message': 'Invalid token!'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        # Pass the current user to the route
        return f(current_user, *args, **kwargs)

    return decorated