from flask import jsonify
from app.models.extension import Extension
from app.services.asterisk_service import AsteriskService

class CallController:
    def __init__(self):
        self.asterisk_service = None

    def get_asterisk_service(self):
        if self.asterisk_service is None:
            self.asterisk_service = AsteriskService()
        return self.asterisk_service

    def initiate_call(self, data):
        try:
            caller = Extension.get_by_id(data['caller'])
            destination = Extension.get_by_id(data['destination'])
            
            if not caller or not destination:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid extension(s)'
                }), 400

            service = self.get_asterisk_service()
            service.originate_call(data['caller'], data['destination'])

            return jsonify({
                'status': 'success',
                'message': 'Call initiated successfully'
            }), 200

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500