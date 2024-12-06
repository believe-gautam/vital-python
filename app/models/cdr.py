
from .base_model import BaseModel


class CDR(BaseModel):
    @classmethod
    def get_user_calls(cls, extension, start_date=None, end_date=None):
        """Get call records for a specific extension"""
        query = """
        SELECT 
            calldate,
            src as source,
            dst as destination,
            duration,
            billsec as billing_seconds,
            disposition,
            uniqueid
        FROM cdr 
        WHERE (src = %s OR dst = %s)
        """
        params = [extension, extension]
        
        if start_date and end_date:
            query += " AND calldate BETWEEN %s AND %s"
            params.extend([start_date, end_date])
            
        query += " ORDER BY calldate DESC"
        return cls.execute_query(query, tuple(params))

    @classmethod
    def get_call_stats(cls, extension, start_date=None, end_date=None):
        """Get call statistics for a specific extension"""
        query = """
        SELECT 
            COUNT(*) as total_calls,
            SUM(CASE WHEN disposition = 'ANSWERED' THEN 1 ELSE 0 END) as answered_calls,
            SUM(duration) as total_duration,
            AVG(CASE WHEN disposition = 'ANSWERED' THEN duration ELSE NULL END) as avg_call_duration
        FROM cdr 
        WHERE (src = %s OR dst = %s)
        """
        params = [extension, extension]
        
        if start_date and end_date:
            query += " AND calldate BETWEEN %s AND %s"
            params.extend([start_date, end_date])
            
        return cls.execute_single(query, tuple(params))
    

    