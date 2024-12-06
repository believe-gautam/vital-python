# controllers/schedule_controller.py
from flask import jsonify
from app.models.call_schedule import CallSchedule
from app.models.extension import Extension
from datetime import datetime
from app.services.asterisk_service import AsteriskService

class ScheduleController:
    def __init__(self):
        self.asterisk_service = AsteriskService()

    def create_schedule(self, data):
        try:
            # Validate extensions exist
            print('================== here we are');
            print(data)
            caller =  Extension.get_by_id(data['source_extension'])
            destination =  Extension.get_by_id(data['destination_extension'])
            
            if not caller or not destination:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid extension(s)'
                }), 400

            # Parse schedule time
            try:
                schedule_time = datetime.fromisoformat(data['scheduled_time'])
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid schedule time format'
                }), 400
            print('we reach to the point')
            print(
                data['source_extension'],
                data['destination_extension'],
                schedule_time,
                'scheduled_time'
            )
            # Create schedule
            CallSchedule.create(
                data['source_extension'],
                data['destination_extension'],
                schedule_time,
                'scheduled_time'
            )
            
            print({
                'status': 'success',
                'message': 'Call scheduled successfully'
            })

            return jsonify({
                'status': 'success',
                'message': 'Call scheduled successfully'
            }), 201

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    def get_schedules(self, extension=None):
        try:
            schedules = CallSchedule.get_all(extension)
            return jsonify({
                'status': 'success',
                'schedules': schedules
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    def cancel_schedule(self, schedule_id):
        try:
            schedule = CallSchedule.get_by_id(schedule_id)
            if not schedule:
                return jsonify({
                    'status': 'error',
                    'message': 'Schedule not found'
                }), 404

            CallSchedule.update_status(schedule_id, 'cancelled')
            return jsonify({
                'status': 'success',
                'message': 'Schedule cancelled successfully'
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
