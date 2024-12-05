# routes/api.py
from flask import Blueprint, request
from app.controllers.schedule_controller import ScheduleController
from app.controllers.call_controller import CallController
from app.middleware.auth import token_required
from flask import jsonify






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
    
# Example usage in app.py
def register_routes(app):
    app.register_blueprint(api, url_prefix='/api')