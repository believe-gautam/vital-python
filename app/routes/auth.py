from flask import Blueprint, request, jsonify
from app.models.user import User
from app.utils.database import init_db
from app import get_db
from app.utils.email import send_email
import threading
import random
import string
from app.middleware.auth import token_required

from app.controllers.extension_controller import ExtensionController

# Initialize controllers
extension_controller = ExtensionController()

auth_bp = Blueprint('auth', __name__)

@auth_bp.before_request
def setup_database():
    init_db()

    

def send_email_async(to_email, subject, body):
    """
    Background thread for sending email asynchronously.
    """
    try:
        send_email(to_email, subject, body)
        print("Email sent successfully.")
    except Exception as e:
         print(f"Email sending failed for {to_email}: {e}")


# register Request API
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not all(k in data for k in ['username', 'email']):
        return jsonify({'error': 'Missing required fields'}), 400

    username = data['username']
    email = data['email']

    otp = ''.join(random.choices(string.digits, k=6))
    if User.create_user(username, email, otp):
        email_thread = threading.Thread(
            target=send_email_async, 
            args=(email, "Your OTP Verification Code", f"Your OTP is: {otp}")
        )
        email_thread.start()  

        return jsonify({'message': 'User registered successfully. Check your email for OTP'}), 200
    else:
        return jsonify({'error': 'Email already exists'}), 409


# register Request API
@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    try: 
        data = request.get_json()
        data['otp'] = ''.join(random.choices(string.digits, k=6))
        print(data)
        if(User.resend_otp(data)):
            email = data['email']
            otp = data['otp']
            email_thread = threading.Thread(
                target=send_email_async, 
                args=(email, "Your OTP Verification Code", f"Your OTP is: {otp}")
            )
            email_thread.start()
            return jsonify({'message': 'OTP Sent Successfully'}), 200
        else: 
            return jsonify({'error': 'Email does not exists'}), 409
    except Exception as e:
        return jsonify({'error': e}), 409




# verify-otp Request API
@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    response = User.verify_otp(email, otp)
    if response['status']:
        user  = response['user_data']
        token  = User.generate_token(user['id']); 
        return jsonify({"message": "OTP verified successfully.","token":token}), 200
    else:
        return jsonify({"error": "Invalid or expired OTP.","token":''}), 400

@auth_bp.route("/check-email", methods=['GET'])
def checkEmail():
        email = 'bobby786b@gmail.com'
        otp = 121212121
        email_thread = threading.Thread(
        target=send_email_async, 
        args=(email, "Your OTP Verification Code", f"Your OTP is: {otp}")
        )
        email_thread.start()  
        print(email_thread)
        return jsonify({"message": "Email Send Successfully."}), 200


# set-password Request API
@auth_bp.route('/set-password', methods=['POST'])
@token_required
def set_password(current_user):
    data = request.get_json()
    user_id  = current_user['id']
    if not all(k in data for k in ['email', 'new_password', 'confirm_password']):
        return jsonify({'error': 'Missing required fields'}), 400

    if data['new_password'] != data['confirm_password']:
        return jsonify({'error': 'Passwords do not match'}), 400
    if User.set_password(data['email'], data['new_password'],user_id):
        data['user_id'] = user_id
        response = extension_controller.create_single_ext(data)
        return jsonify({'message': 'Password set successfully. You can now login',"response":response}), 200
    else:
        return jsonify({'error': 'Failed to set password. Verify OTP first'}), 400


# @auth_bp.route('/create-ext', methods=['GET'])
# @token_required
# def create_ext(current_user):
#     data['user_id']   = current_user['id']
#     print(data)
#     response = extension_controller.create_single_ext(data)
#     if(response):
#         return jsonify({'message': 'Password set successfully. You can now login'}), 200
#     else:
#         return jsonify({'error': 'Failed to set password. Verify OTP first'}), 400

@auth_bp.route('/create-ext', methods=['GET'])
@token_required
def create_ext(current_user):
    # Ensure that current_user is not None and contains the 'id' field
    if not current_user or 'id' not in current_user:
        return jsonify({'error': 'Invalid user'}), 400

    # Initialize the data dictionary
    data = {}

    # Add user_id to the data dictionary
    data['user_id'] = current_user['id']
    print(data)

    # Call the extension controller to create the extension
    response = extension_controller.create_single_ext(data)

    # Check if the response indicates success or failure
    if response:
        return jsonify({'message': 'Password set successfully. You can now login'}), 200
    else:
        return jsonify({'error': 'Failed to set password. Verify OTP first'}), 400

# login Request API
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400

    user = User.authenticate(data['email'], data['password'])
    print('---------------------- here ')
    print(user)
    if user:
        token = User.generate_token(user['id'])
        return jsonify({
            'message': 'Login successful',
            'token': token
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401





def send_email_async(to_email, subject, body):
    """
    Background thread for sending email asynchronously.
    """
    try:
        send_email(to_email, subject, body)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")

# Forget Password Request API
@auth_bp.route('/forget-password', methods=['POST'])
def forget_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    # Get user by email
    user = User.get_user_by_email(email)
    if not user:
        return jsonify({'error': 'User with this email does not exist'}), 404

    # Generate reset token
    token = User.generate_reset_token(email)

    # Create reset link
    reset_link = f"http://localhost:5000/reset-password/{token}"
    

    # Send email asynchronously
    email_thread = threading.Thread(
        target=send_email_async, 
        args=(email, "Password Reset Request", f"Click the link to reset your password: {reset_link}")
    )
    email_thread.start()

    return jsonify({'message': 'Password reset email sent successfully'}), 200

# Reset Password API
@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    data = request.get_json()
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not new_password or not confirm_password:
        return jsonify({'error': 'Both password fields are required'}), 400

    if new_password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    # Verify token and reset password
    if User.reset_password(token, new_password):
        return jsonify({'message': 'Password reset successful'}), 200
    else:
        return jsonify({'error': 'Invalid or expired token'}), 400