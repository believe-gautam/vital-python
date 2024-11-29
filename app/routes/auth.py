from flask import Blueprint, request, jsonify
from app.models.user import User
from app.utils.database import init_db

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
    
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.create(data['username'], data['email'], data['password']):
        return jsonify({'message': 'User registered successfully'}), 201
    else:
        return jsonify({'error': 'Username or email already exists'}), 409

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    user = User.authenticate(data['email'], data['password'])
    if user:
        token = User.generate_token(user['id'])
        return jsonify({
            'message': 'Login successful',
            'token': token
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401