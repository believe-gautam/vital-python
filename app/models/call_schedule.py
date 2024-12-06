from app import get_db
from datetime import datetime

class CallSchedule:
    @staticmethod
    def create(caller_extension, destination_extension, schedule_time, description=None, user_id=None):
        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            # First verify if extensions exist
            cursor.execute(
                "SELECT id FROM extensions WHERE extension_number = %s", 
                (caller_extension,)  # Note the comma to make it a tuple
            )
            source_ext = cursor.fetchone()
            
            cursor.execute(
                "SELECT id FROM extensions WHERE extension_number = %s", 
                (destination_extension,)  # Note the comma to make it a tuple
            )
            dest_ext = cursor.fetchone()

            if not source_ext or not dest_ext:
                return None  # One or both extensions don't exist


            # Insert the scheduled call
            cursor.execute(
                """INSERT INTO scheduled_calls 
                (user_id, source_extension_id, destination_extension_id, scheduled_time, notes, status)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, source_ext['id'], dest_ext['id'], schedule_time, description, 'pending')
            )
            
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating call schedule: {e}")
            db.rollback()
            return None
        finally:
            cursor.close()


    @staticmethod
    def get_all(extension=None, user_id=None):
        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            if extension:
                cursor.execute('''
                    SELECT sc.*, 
                           e1.extension_number as source_number,
                           e2.extension_number as destination_number
                    FROM scheduled_calls sc
                    JOIN extensions e1 ON sc.source_extension_id = e1.id
                    JOIN extensions e2 ON sc.destination_extension_id = e2.id
                    WHERE e1.extension_number = %s OR e2.extension_number = %s
                    ORDER BY scheduled_time
                ''', (extension, extension))
            elif user_id:
                cursor.execute('''
                    SELECT sc.*, 
                           e1.extension_number as source_number,
                           e2.extension_number as destination_number
                    FROM scheduled_calls sc
                    JOIN extensions e1 ON sc.source_extension_id = e1.id
                    JOIN extensions e2 ON sc.destination_extension_id = e2.id
                    WHERE sc.user_id = %s
                    ORDER BY scheduled_time
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT sc.*, 
                           e1.extension_number as source_number,
                           e2.extension_number as destination_number
                    FROM scheduled_calls sc
                    JOIN extensions e1 ON sc.source_extension_id = e1.id
                    JOIN extensions e2 ON sc.destination_extension_id = e2.id
                    ORDER BY scheduled_time
                ''')
            
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching call schedules: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def get_by_id(schedule_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute('''
                SELECT sc.*, 
                       e1.extension_number as source_number,
                       e2.extension_number as destination_number
                FROM scheduled_calls sc
                JOIN extensions e1 ON sc.source_extension_id = e1.id
                JOIN extensions e2 ON sc.destination_extension_id = e2.id
                WHERE sc.id = %s
            ''', (schedule_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error fetching call schedule: {e}")
            return None
        finally:
            cursor.close()

    @staticmethod
    def update_status(schedule_id, status, retry_count=None):
        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            if retry_count is not None:
                cursor.execute('''
                    UPDATE scheduled_calls
                    SET status = %s, 
                        retry_count = %s,
                        updated_at = NOW()
                    WHERE id = %s
                ''', (status, retry_count, schedule_id))
            else:
                cursor.execute('''
                    UPDATE scheduled_calls
                    SET status = %s,
                        updated_at = NOW()
                    WHERE id = %s
                ''', (status, schedule_id))
            
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating call schedule: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()

    @staticmethod
    def get_pending_calls():
        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute('''
                SELECT sc.*, 
                       e1.extension_number as source_number,
                       e2.extension_number as destination_number
                FROM scheduled_calls sc
                JOIN extensions e1 ON sc.source_extension_id = e1.id
                JOIN extensions e2 ON sc.destination_extension_id = e2.id
                WHERE sc.status = 'pending'
                AND sc.scheduled_time <= NOW()
                ORDER BY sc.scheduled_time
            ''')
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching pending calls: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def delete_schedule(schedule_id, user_id=None):
        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            if user_id:
                cursor.execute('''
                    DELETE FROM scheduled_calls
                    WHERE id = %s AND user_id = %s
                ''', (schedule_id, user_id))
            else:
                cursor.execute('DELETE FROM scheduled_calls WHERE id = %s', (schedule_id,))
            
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting call schedule: {e}")
            db.rollback()
            return False
        finally:
            cursor.close()