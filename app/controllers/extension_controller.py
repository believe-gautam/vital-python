from flask import jsonify
from app.models.extension import Extension
import re

class ExtensionController:
    def create_extension(self, data):
        try:
            # Validate extension format
            if not re.match(r'^\d{6}$', data['extension']):
                return jsonify({
                    'status': 'error',
                    'message': 'Extension must be 6 digits'
                }), 400

            # Validate password
            if len(data['password']) < 8:
                return jsonify({
                    'status': 'error',
                    'message': 'Password must be at least 8 characters'
                }), 400

            # Extension.create(data)
            return jsonify({
                'status': 'success',
                'message': 'Extension created successfully'
            }), 201
        except Exception as e:
            print(e)
            return jsonify({
                'status': 'error1',
                'message': str(e)
            }), 500

    def update_extension(self, extension_id, data):
        try:
            Extension.update(extension_id, data)
            return jsonify({
                'status': 'success',
                'message': 'Extension updated successfully'
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    def delete_extension(self, extension_id):
        try:
            Extension.delete(extension_id)
            return jsonify({
                'status': 'success',
                'message': 'Extension deleted successfully'
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    def get_extensions(self):
        try:
            extensions = Extension.get_all()
            return jsonify({
                'status': 'success',
                'extensions': extensions
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
