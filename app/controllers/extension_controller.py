from flask import jsonify
from app.models.extension import Extension
import re
import random


class ExtensionController:
    @staticmethod
    def generate_extension():
        # Increment and return the next extension
        ExtensionController.last_extension += 1
        if ExtensionController.last_extension > 299999:
            raise Exception("No more extensions available")
        return str(ExtensionController.last_extension)

    @staticmethod
    def generate_password(length=12):
        # Generate a random password
        import string
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def create_extension(self, data):
        try:
            Extension.create(data)
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

    def create_single_ext(self, data):
        try:
            Extension.single_ext_create(data)
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


    def get_user_ext(self,user_id):
        try:
            extensions = Extension.get_user_extensions(user_id)
            if(len(extensions) > 0 ): 
                return jsonify({
                    'status': 'success',
                    'extensions': extensions[0]
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'extensions': {},
                    'message': 'No Extension Found'
                }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
