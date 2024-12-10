from app import get_db
from datetime import datetime

class Extension:
    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT e.*, 
                       a.password as auth_password,
                       aor.max_contacts,
                       aor.qualify_frequency
                FROM ps_endpoints e
                LEFT JOIN ps_auths a ON e.id = a.id
                LEFT JOIN ps_aors aor ON e.id = aor.id
                ORDER BY e.id
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching extensions: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def get_by_id(extension_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        print('--------------- we come inside the get_by_id')
        try:
            cursor.execute("""
                SELECT e.*, 
                       a.password as auth_password,
                       aor.max_contacts,
                       aor.qualify_frequency
                FROM ps_endpoints e
                LEFT JOIN ps_auths a ON e.id = a.id
                LEFT JOIN ps_aors aor ON e.id = aor.id
                WHERE e.id = %s
            """, (extension_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error fetching extension: {e}")
            return None
        finally:
            cursor.close()

    @staticmethod
    def create(extension_data):
        print('Check Here')
        print(extension_data)
        db = get_db()
        cursor = db.cursor(dictionary=True)
        print('This is testing')
        try:
            # Check if extension already exists
            cursor.execute("SELECT id FROM ps_endpoints WHERE id = %s", 
                         (extension_data['extension'],))
            if cursor.fetchone():
                raise Exception("Extension already exists")
            
            # Insert endpoint
            cursor.execute("""
                INSERT INTO ps_endpoints 
                (id, transport, aors, auth, context, disallow, allow, direct_media)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                extension_data['extension'],
                'transport-udp',
                extension_data['extension'],
                extension_data['extension'],
                'testing',
                'all',
                'opus,ulaw,alaw',
                'no'
            ))

            # Insert authentication
            cursor.execute("""
                INSERT INTO ps_auths 
                (id, auth_type, password, username)
                VALUES (%s, %s, %s, %s)
            """, (
                extension_data['extension'],
                'userpass',
                extension_data['password'],
                extension_data['extension']
            ))

            # Insert AOR (Address of Record)
            cursor.execute("""
                INSERT INTO ps_aors 
                (id, max_contacts, qualify_frequency)
                VALUES (%s, %s, %s)
            """, (
                extension_data['extension'],
                1,
                30
            ))

            db.commit()
            return extension_data['extension']

        except Exception as e:
            db.rollback()
            print(f"Error creating extension: {e}")
            raise
        finally:
            cursor.close()

    @staticmethod
    def update(extension_id, extension_data):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        try:
            updates = []
            if 'password' in extension_data:
                cursor.execute("""
                    UPDATE ps_auths
                    SET password = %s
                    WHERE id = %s
                """, (extension_data['password'], extension_id))
                updates.append('password')

            if 'context' in extension_data:
                cursor.execute("""
                    UPDATE ps_endpoints
                    SET context = %s
                    WHERE id = %s
                """, (extension_data['context'], extension_id))
                updates.append('context')

            if updates:
                db.commit()
                return True
            return False

        except Exception as e:
            db.rollback()
            print(f"Error updating extension: {e}")
            return False
        finally:
            cursor.close()

    @staticmethod
    def delete(extension_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        try:
            # Delete in specific order due to foreign key constraints
            tables = ['ps_auths', 'ps_aors', 'ps_endpoints']
            
            for table in tables:
                cursor.execute(f"DELETE FROM {table} WHERE id = %s", (extension_id,))
            
            db.commit()
            return True

        except Exception as e:
            db.rollback()
            print(f"Error deleting extension: {e}")
            return False
        finally:
            cursor.close()

    @staticmethod
    def check_availability(extension_number):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM ps_endpoints 
                WHERE id = %s
            """, (extension_number,))
            
            result = cursor.fetchone()
            return result['count'] == 0
            
        except Exception as e:
            print(f"Error checking extension availability: {e}")
            return False
        finally:
            cursor.close()

    @staticmethod
    def get_user_extensions(user_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT e.*, ue.is_primary 
                FROM ps_endpoints e
                JOIN user_extensions_mapping ue ON e.id = ue.extension_id
                WHERE ue.user_id = %s
                ORDER BY e.id
            """, (user_id,))
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Error fetching user extensions: {e}")
            return []
        finally:
            cursor.close()