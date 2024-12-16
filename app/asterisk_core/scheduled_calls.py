# app/models/scheduled_calls.py
from app.models.base_model import BaseModel

class ScheduledCalls(BaseModel):
    @classmethod
    def get_pending_calls(cls):
        """Get all pending calls that are due for execution"""
        query = """
        SELECT 
            id,
            user_id,
            source_extension,
            scheduled_time,
            status,
            notes,
            retry_count
        FROM scheduled_calls 
        WHERE status = 'pending' 
        AND scheduled_time <= NOW() 
        AND retry_count < 3
        """
        return cls.execute_query(query)

    @classmethod
    def update_call_status(cls, call_id, status, retry_count=None):
        """Update the status and retry count of a scheduled call"""
        query = """
        UPDATE scheduled_calls 
        SET 
            status = %s,
            retry_count = COALESCE(%s, retry_count),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        return cls.execute_update(query, (status, retry_count, call_id))

