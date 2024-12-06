from flask import jsonify
from app.models.cdr import CDR
from datetime import datetime

class CDRController:
    def get_call_history(self, extension, start_date=None, end_date=None):
        try:
            calls = CDR.get_user_calls(extension, start_date, end_date)
            stats = CDR.get_call_stats(extension, start_date, end_date)
            
            return jsonify({
                'status': 'success',
                'calls': calls,
                'statistics': {
                    'total_calls': stats['total_calls'],
                    'answered_calls': stats['answered_calls'],
                    'total_duration': stats['total_duration'],
                    'average_duration': float(stats['avg_call_duration']) if stats['avg_call_duration'] else 0
                }
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
        
