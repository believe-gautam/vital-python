# routes/api.py
from flask import Blueprint, request
from app.controllers.schedule_controller import ScheduleController
from app.controllers.call_controller import CallController
from app.middleware.auth import token_required
from flask import jsonify

import re
from datetime import datetime


from app.controllers.extension_controller import ExtensionController
from app.controllers.cdr_controller import CDRController

extension_controller = ExtensionController()
cdr_controller = CDRController()



api = Blueprint('api', __name__)
schedule_controller = ScheduleController()
call_controller = CallController()

@api.route("/",methods=['GET'])
def base_method():
    return jsonify({
                    'status': 'success',
                    'message': 'Server Running Fine'
                }), 200



# Schedule routes
# @api.route('/schedules', methods=['POST'])
# def create_schedule():
#     return schedule_controller.create_schedule(request.json)

# @api.route('/schedules', methods=['GET'])
# def get_schedules():
#     extension = request.args.get('extension')
#     return schedule_controller.get_schedules(extension)

# @api.route('/schedules/<int:schedule_id>', methods=['DELETE'])
# def cancel_schedule(schedule_id):
#     return schedule_controller.cancel_schedule(schedule_id)

# # Call routes
# @api.route('/calls', methods=['POST'])
# def initiate_call():
#     return call_controller.initiate_call(request.json)



# Protected routes
@api.route('/schedules', methods=['POST'])
@token_required
def create_schedule(current_user):
    return schedule_controller.create_schedule(request.json)

@api.route('/schedules', methods=['GET'])
@token_required
def get_schedules(current_user):
    extension = request.args.get('extension')
    return schedule_controller.get_schedules(extension)

@api.route('/schedules/<int:schedule_id>', methods=['DELETE'])
@token_required
def cancel_schedule(current_user, schedule_id):
    return schedule_controller.cancel_schedule(schedule_id)

@api.route('/calls', methods=['POST'])
@token_required
def initiate_call(current_user):
    return call_controller.initiate_call(request.json)




# Extension management routes
@api.route('/extensions', methods=['POST'])
@token_required
def create_extension(current_user):
    return extension_controller.create_extension(request.json)

@api.route('/extensions/<extension_id>', methods=['PUT'])
@token_required
def update_extension(current_user, extension_id):
    return extension_controller.update_extension(extension_id, request.json)

@api.route('/extensions/<extension_id>', methods=['DELETE'])
@token_required
def delete_extension(current_user, extension_id):
    return extension_controller.delete_extension(extension_id)

@api.route('/extensions', methods=['GET'])
@token_required
def get_extensions(current_user):
    return extension_controller.get_extensions()

# Call reporting routes
@api.route('/calls/history', methods=['GET'])
@token_required
def get_call_history(current_user):
    extension = request.args.get('extension')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    return cdr_controller.get_call_history(extension, start_date, end_date)

# Example usage in app.py
def register_routes(app):
    app.register_blueprint(api, url_prefix='/api')