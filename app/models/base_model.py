# models/base_model.py
from app import get_db

class BaseModel:
    @classmethod
    def execute_query(cls, query, params=None):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @classmethod
    def execute_single(cls, query, params=None):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            db.commit()
            return result
        finally:
            cursor.close()
