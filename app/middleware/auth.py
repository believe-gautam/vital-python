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
                token = auth_header.split(" ")[1]  # Remove 'Bearer ' prefix
            except IndexError:
                token = auth_header
                
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
            
        try:
            # Decode token
            data = jwt.decode(
                token,
                os.getenv('JWT_SECRET_KEY'),
                algorithms=["HS256"]
            )
            
            # Get user_id from token payload
            user_id = data.get('user_id')  # Using get() method instead of direct access
            if user_id is None:
                return jsonify({'message': 'Invalid token: missing user_id'}), 401
                
            # Convert to int only if it's a string
            if isinstance(user_id, str):
                user_id = int(user_id)
                
            # Pass user_id directly, not as a dictionary
            current_user = User.get_by_id(user_id)
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        except ValueError as e:
            return jsonify({'message': f'Invalid user_id format: {str(e)}'}), 401
        except Exception as e:
            return jsonify({'message': f'Error processing token: {str(e)}'}), 401
            
        # Pass the user to the route
        return f(current_user, *args, **kwargs)
    return decorated