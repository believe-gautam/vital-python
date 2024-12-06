from datetime import datetime
from .base_model import BaseModel

class CallSchedule(BaseModel):
    @classmethod
    def create(cls, caller_extension, destination_extension, schedule_time, description=None):
        query = """
        INSERT INTO call_schedules 
        (caller_extension, destination_extension, schedule_time, description) 
        VALUES (%s, %s, %s, %s)
        """
        return cls.execute_query(
            query, 
            (caller_extension, destination_extension, schedule_time, description)
        )

    @classmethod
    def get_all(cls, extension=None):
        if extension:
            query = """
            SELECT * FROM call_schedules 
            WHERE caller_extension = %s OR destination_extension = %s 
            ORDER BY schedule_time
            """
            return cls.execute_query(query, (extension, extension))
        else:
            query = "SELECT * FROM call_schedules ORDER BY schedule_time"
            return cls.execute_query(query)

    @classmethod
    def get_by_id(cls, schedule_id):
        query = "SELECT * FROM call_schedules WHERE id = %s"
        return cls.execute_single(query, (schedule_id,))

    @classmethod
    def update_status(cls, schedule_id, status, retry_count=None):
        if retry_count is not None:
            query = """
            UPDATE call_schedules 
            SET status = %s, retry_count = %s, updated_at = NOW() 
            WHERE id = %s
            """
            return cls.execute_query(query, (status, retry_count, schedule_id))
        else:
            query = """
            UPDATE call_schedules 
            SET status = %s, updated_at = NOW() 
            WHERE id = %s
            """
            return cls.execute_query(query, (status, schedule_id))