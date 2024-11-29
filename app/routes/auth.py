from flask import Blueprint, request, jsonify
from app.models.user import User
from app.utils.database import init_db
from app import get_db
auth_bp = Blueprint('auth', __name__)

@auth_bp.before_request
def setup_database():
    init_db()

@auth_bp.route('/', methods=['GET'])
def check():
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not all(k in data for k in ['mobile_number', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.create(data['mobile_number'], data['password']):
        return jsonify({'message': 'User registered successfully'}), 201
    else:
        return jsonify({'error': 'Mobile number already exists'}), 409

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(k in data for k in ['mobile_number', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    user = User.authenticate(data['mobile_number'], data['password'])
    if user:
        token = User.generate_token(user['id'])
        return jsonify({
            'message': 'Login successful',
            'token': token
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
    

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    
    if 'mobile_number' not in data:
        return jsonify({'error': 'Mobile number is required'}), 400
    
    mobile_number = data['mobile_number']
    
    # Check if mobile number exists
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE mobile_number = %s', (mobile_number,))
    user = cursor.fetchone()
    cursor.close()
    
    if not user:
        return jsonify({'error': 'Mobile number not found'}), 404
    
    # Generate OTP
    otp = User.generate_otp(mobile_number)
    
    if otp:
        # TODO: In real application, send OTP via SMS
        return jsonify({
            'message': 'OTP generated successfully',
            'otp': otp  # Only for testing/demonstration
        }), 200
    else:
        return jsonify({'error': 'Failed to generate OTP'}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    
    if not all(k in data for k in ['mobile_number', 'otp']):
        return jsonify({'error': 'Mobile number and OTP are required'}), 400
    
    mobile_number = data['mobile_number']
    otp = data['otp']
    
    # Verify OTP
    if User.verify_otp(mobile_number, otp):
        return jsonify({
            'message': 'OTP verified successfully',
            'can_reset_password': True
        }), 200
    else:
        return jsonify({'error': 'Invalid or expired OTP'}), 400
    




@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    
    if not all(k in data for k in ['mobile_number', 'new_password']):
        return jsonify({'error': 'Mobile number and new password are required'}), 400
    
    mobile_number = data['mobile_number']
    new_password = data['new_password']
    
    # Reset password (only if OTP was previously verified)
    if User.reset_password_with_otp(mobile_number, new_password):
        return jsonify({'message': 'Password reset successful'}), 200
    else:
        return jsonify({'error': 'Password reset failed. Verify OTP first.'}), 400
    

    