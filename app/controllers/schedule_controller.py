# # controllers/schedule_controller.py
# from flask import jsonify
# from app.models.call_schedule import CallSchedule
# from app.models.extension import Extension
# from datetime import datetime
# from app.services.asterisk_service import AsteriskService

# class ScheduleController:
#     def __init__(self):
#         self.asterisk_service = AsteriskService()

#     def create_schedule(self, data):
#         try:
#             # Validate extensions exist
#             print('================== here we are');
#             print(data)
#             caller =  Extension.get_by_id(data['source_extension'])
#             destination =  Extension.get_by_id(data['destination_extension'])
            
#             if not caller or not destination:
#                 return jsonify({
#                     'status': 'error',
#                     'message': 'Invalid extension(s)'
#                 }), 400

#             # Parse schedule time
#             try:
#                 schedule_time = datetime.fromisoformat(data['scheduled_time'])
#             except ValueError:
#                 return jsonify({
#                     'status': 'error',
#                     'message': 'Invalid schedule time format'
#                 }), 400
#             print('we reach to the point')
#             print(
#                 data['source_extension'],
#                 data['destination_extension'],
#                 schedule_time,
#                 'scheduled_time'
#             )
#             # Create schedule
#             CallSchedule.create(
#                 data['source_extension'],
#                 data['destination_extension'],
#                 schedule_time,
#                 'scheduled_time'
#             )
            
#             print({
#                 'status': 'success',
#                 'message': 'Call scheduled successfully'
#             })

#             return jsonify({
#                 'status': 'success',
#                 'message': 'Call scheduled successfully'
#             }), 201

#         except Exception as e:
#             return jsonify({
#                 'status': 'error',
#                 'message': str(e)
#             }), 500

#     def get_schedules(self, extension=None):
#         try:
#             schedules = CallSchedule.get_all(extension)
#             return jsonify({
#                 'status': 'success',
#                 'schedules': schedules
#             }), 200
#         except Exception as e:
#             return jsonify({
#                 'status': 'error',
#                 'message': str(e)
#             }), 500

#     def cancel_schedule(self, schedule_id):
#         try:
#             schedule = CallSchedule.get_by_id(schedule_id)
#             if not schedule:
#                 return jsonify({
#                     'status': 'error',
#                     'message': 'Schedule not found'
#                 }), 404

#             CallSchedule.update_status(schedule_id, 'cancelled')
#             return jsonify({
#                 'status': 'success',
#                 'message': 'Schedule cancelled successfully'
#             }), 200
#         except Exception as e:
#             return jsonify({
#                 'status': 'error',
#                 'message': str(e)
#             }), 500



# app/controllers/schedule_controller.py
from flask import jsonify
from app.models.call_schedule import CallSchedule
from datetime import datetime

class ScheduleController:
    def create_schedule(self, data):
        try:
            required_fields = ['caller_extension', 'destination_extension', 'schedule_time']
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'Missing required fields'}), 400

            try:
                schedule_time = datetime.strptime(data['schedule_time'], '%Y-%m-%d %H:%M:%S')
                if schedule_time < datetime.now():
                    return jsonify({'error': 'Schedule time must be in the future'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid datetime format. Use YYYY-MM-DD HH:MM:SS'}), 400

            schedule_id = CallSchedule.create(
                caller_extension=data['caller_extension'],
                destination_extension=data['destination_extension'],
                schedule_time=schedule_time,
                description=data.get('description'),
                user_id=data.get('user_id')
            )

            if schedule_id:
                return jsonify({
                    'message': 'Call scheduled successfully',
                    'schedule_id': schedule_id
                }), 201
            return jsonify({'error': 'Failed to create schedule'}), 400

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def get_schedules(self, extension=None, user_id=None):
        try:
            schedules = CallSchedule.get_all(extension=extension, user_id=user_id)
            return jsonify({
                'schedules': schedules,
                'count': len(schedules)
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def get_schedule(self, schedule_id, user_id):
        try:
            schedule = CallSchedule.get_by_id(schedule_id)
            if not schedule:
                return jsonify({'error': 'Schedule not found'}), 404
            
            if schedule['user_id'] != user_id:
                return jsonify({'error': 'Unauthorized access'}), 403
                
            return jsonify(schedule), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def cancel_schedule(self, schedule_id, user_id):
        try:
            schedule = CallSchedule.get_by_id(schedule_id)
            if not schedule:
                return jsonify({'error': 'Schedule not found'}), 404
                
            if schedule['user_id'] != user_id:
                return jsonify({'error': 'Unauthorized access'}), 403

            if CallSchedule.delete_schedule(schedule_id, user_id):
                return jsonify({'message': 'Schedule cancelled successfully'}), 200
            return jsonify({'error': 'Failed to cancel schedule'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def update_schedule(self, schedule_id, data):
        try:
            schedule = CallSchedule.get_by_id(schedule_id)
            if not schedule:
                return jsonify({'error': 'Schedule not found'}), 404
                
            if schedule['user_id'] != data.get('user_id'):
                return jsonify({'error': 'Unauthorized access'}), 403

            status = data.get('status')
            if not status:
                return jsonify({'error': 'Status is required'}), 400

            if CallSchedule.update_status(schedule_id, status, data.get('retry_count')):
                return jsonify({'message': 'Schedule updated successfully'}), 200
            return jsonify({'error': 'Failed to update schedule'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def get_pending_schedules(self, user_id):
        try:
            pending_calls = CallSchedule.get_pending_calls()
            user_calls = [call for call in pending_calls if call['user_id'] == user_id]
            
            return jsonify({
                'pending_schedules': user_calls,
                'count': len(user_calls)
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500