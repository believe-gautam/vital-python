# app/models/extension_schedule.py
from app.models.base_model import BaseModel
from datetime import datetime

class ExtensionSchedule(BaseModel):
    @classmethod
    def get_available_extensions(cls, scheduled_time):
        """Get all extensions available at specific time"""
        query = """
        SELECT 
            extension_number,
            user_id,
            scheduled_time,
            status
        FROM extension_schedules
        WHERE scheduled_time = %s
        AND status = 'available'
        """
        return cls.execute_query(query, (scheduled_time,))

    @classmethod
    def update_extension_status(cls, extension_number, status):
        """Update extension status after call pairing"""
        query = """
        UPDATE extension_schedules
        SET 
            status = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE extension_number = %s
        """
        return cls.execute_update(query, (status, extension_number))


