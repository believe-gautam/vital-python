# routes/api.py
from flask import Blueprint, request, jsonify
from app.controllers.schedule_controller import ScheduleController
from app.controllers.call_controller import CallController
from app.middleware.auth import token_required
from datetime import datetime
from app.controllers.extension_controller import ExtensionController
from app.controllers.cdr_controller import CDRController

# Initialize controllers
extension_controller = ExtensionController()
cdr_controller = CDRController()
schedule_controller = ScheduleController()
call_controller = CallController()

api = Blueprint('api', __name__)

@api.route("/", methods=['GET'])
def base_method():
    return jsonify({
        'status': 'success',
        'message': 'Server Running Fine'
    }), 200

# Schedule routes
@api.route('/schedules', methods=['POST'])
@token_required
def create_schedule(current_user):
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Add user_id to the request data
        data['user_id'] = current_user['id']
        return schedule_controller.create_schedule(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/schedules', methods=['GET'])
@token_required
def get_schedules(current_user):
    try:
        extension = request.args.get('extension')
        user_id = current_user['id']
        return schedule_controller.get_schedules(extension, user_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/schedules/<int:schedule_id>', methods=['DELETE'])
@token_required
def cancel_schedule(current_user, schedule_id):
    try:
        return schedule_controller.cancel_schedule(schedule_id, current_user['id'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Call routes
@api.route('/calls', methods=['POST'])
@token_required
def initiate_call(current_user):
    try:
        data = request.json
        data['user_id'] = current_user['id']
        return call_controller.initiate_call(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Extension management routes
@api.route('/extensions', methods=['POST'])
@token_required
def create_extension(current_user):
    try:
        data = request.json
        data['user_id'] = current_user['id']
        return extension_controller.create_extension(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 200

@api.route('/extensions/<extension_id>', methods=['PUT'])
@token_required
def update_extension(current_user, extension_id):
    try:
        return extension_controller.update_extension(extension_id, request.json)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/extensions/<extension_id>', methods=['DELETE'])
@token_required
def delete_extension(current_user, extension_id):
    try:
        return extension_controller.delete_extension(extension_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/extensions', methods=['GET'])
@token_required
def get_extensions(current_user):
    try:
        return extension_controller.get_extensions()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@api.route('/get-ext', methods=['GET'])
@token_required
def get_user_ext(current_user):
    try:
        user_id = current_user['id']
        return extension_controller.get_user_ext(user_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Call reporting routes
@api.route('/calls/history', methods=['GET'])
@token_required
def get_call_history(current_user):
    try:
        extension = request.args.get('extension')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        return cdr_controller.get_call_history(extension, start_date, end_date)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New routes for schedule management
@api.route('/schedules/<int:schedule_id>', methods=['GET'])
@token_required
def get_schedule(current_user, schedule_id):
    try:
        return schedule_controller.get_schedule(schedule_id, current_user['id'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/schedules/<int:schedule_id>', methods=['PUT'])
@token_required
def update_schedule(current_user, schedule_id):
    try:
        data = request.json
        data['user_id'] = current_user['id']
        return schedule_controller.update_schedule(schedule_id, data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/schedules/pending', methods=['GET'])
@token_required
def get_pending_schedules(current_user):
    try:
        return schedule_controller.get_pending_schedules(current_user['id'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def register_routes(app):
    app.register_blueprint(api, url_prefix='/api')