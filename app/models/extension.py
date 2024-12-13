from app import get_db
from datetime import datetime
import random

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

    # @staticmethod
    # def create(extension_data):
    #     print('Check Here')
    #     print(extension_data)
    #     db = get_db()
    #     cursor = db.cursor(dictionary=True)
    #     print('This is testing')
    #     try:
    #         # Check if extension already exists
    #         cursor.execute("SELECT id FROM ps_endpoints WHERE id = %s", 
    #                      (extension_data['extension'],))
    #         if cursor.fetchone():
    #             raise Exception("Extension already exists")
            
    #         # Insert endpoint
    #         cursor.execute("""
    #             INSERT INTO ps_endpoints 
    #             (id, transport, aors, auth, context, disallow, allow, direct_media)
    #             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    #         """, (
    #             extension_data['extension'],
    #             'transport-udp',
    #             extension_data['extension'],
    #             extension_data['extension'],
    #             'testing',
    #             'all',
    #             'opus,ulaw,alaw',
    #             'no'
    #         ))

    #         # Insert authentication
    #         cursor.execute("""
    #             INSERT INTO ps_auths 
    #             (id, auth_type, password, username)
    #             VALUES (%s, %s, %s, %s)
    #         """, (
    #             extension_data['extension'],
    #             'userpass',
    #             extension_data['password'],
    #             extension_data['extension']
    #         ))

    #         # Insert AOR (Address of Record)
    #         cursor.execute("""
    #             INSERT INTO ps_aors 
    #             (id, max_contacts, qualify_frequency)
    #             VALUES (%s, %s, %s)
    #         """, (
    #             extension_data['extension'],
    #             1,
    #             30
    #         ))

    #         db.commit()
    #         return extension_data['extension']

    #     except Exception as e:
    #         db.rollback()
    #         print(f"Error creating extension: {e}")
    #         raise
    #     finally:
    #         cursor.close()


    @staticmethod
    def create(payload_data):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        try:
            # Decode the token to extract user_id (assuming a helper function `decode_token`)
            user_id =payload_data['user_id'] #decode_token(token).get("user_id")
            if not user_id:
                raise Exception("Invalid or missing user_id in token")

            # Retrieve the last extension
            cursor.execute("SELECT id FROM ps_endpoints ORDER BY id DESC LIMIT 1")
            last_extension_row = cursor.fetchone()
            last_extension = int(last_extension_row['id']) if last_extension_row else 200003

            # Generate the new extension
            new_extension = last_extension + 1
            if new_extension > 299999:
                raise Exception("No more extensions available")

            # Generate a random password
            password = ''.join(random.choices(
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*',
                k=12
            ))

            # Static values
            static_values = {
                "transport": "transport-ws",
                "context": "testing",
                "disallow": "all",
                "allow": "opus,ulaw,alaw",
                "direct_media": "no",
                "auth_type": "userpass",
                "max_contacts": 1,
                "qualify_frequency": 30,
                "disable_direct_media_on_nat": "yes",
                "force_rport": "yes",
                "ice_support": "yes",
                "rewrite_contact": "yes",
                "rtp_symmetric": "yes",
                "use_avpf": "yes",
                "media_encryption": "sdes",
                "dtls_verify": "fingerprint",
                "dtls_rekey": "0",
                "dtls_cert_file": "/etc/letsencrypt/live/tcdev.site/fullchain.pem",
                "dtls_private_key": "/etc/letsencrypt/live/tcdev.site/privkey.pem",
                "dtls_setup": "actpass",
                "rtcp_mux": "yes",
                "webrtc": "yes",
            }

            # Check if extension already exists
            cursor.execute("SELECT id FROM ps_endpoints WHERE id = %s", (new_extension,))
            if cursor.fetchone():
                raise Exception("Extension already exists")

            # Insert endpoint
            cursor.execute("""
                INSERT INTO ps_endpoints 
                (id, transport, aors, auth, context, disallow, allow, direct_media,
                 disable_direct_media_on_nat, force_rport, ice_support, rewrite_contact, 
                 rtp_symmetric, use_avpf, media_encryption, dtls_verify, dtls_rekey, 
                 dtls_cert_file, dtls_private_key, dtls_setup, rtcp_mux, webrtc, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                new_extension,
                static_values["transport"],
                new_extension,
                new_extension,
                static_values["context"],
                static_values["disallow"],
                static_values["allow"],
                static_values["direct_media"],
                static_values["disable_direct_media_on_nat"],
                static_values["force_rport"],
                static_values["ice_support"],
                static_values["rewrite_contact"],
                static_values["rtp_symmetric"],
                static_values["use_avpf"],
                static_values["media_encryption"],
                static_values["dtls_verify"],
                static_values["dtls_rekey"],
                static_values["dtls_cert_file"],
                static_values["dtls_private_key"],
                static_values["dtls_setup"],
                static_values["rtcp_mux"],
                static_values["webrtc"],
                user_id
            ))

            # Insert authentication
            cursor.execute("""
                INSERT INTO ps_auths 
                (id, auth_type, password, username)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                new_extension,
                static_values["auth_type"],
                password,
                new_extension
            ))

            # Insert AOR (Address of Record)
            cursor.execute("""
                INSERT INTO ps_aors 
                (id, max_contacts, qualify_frequency)
                VALUES (%s, %s, %s, %s)
            """, (
                new_extension,
                static_values["max_contacts"],
                static_values["qualify_frequency"]
            ))

            # Commit the transaction
            db.commit()

            # Return the new extension details
            return {
                "extension": new_extension,
                "password": password,
                "user_id": user_id
            }

        except Exception as e:
            db.rollback()
            print(f"Error creating extension: {e}")
            raise
        finally:
            cursor.close()


    @staticmethod
    def single_ext_create(payload_data):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        try:
            # Decode the token to extract user_id (assuming a helper function `decode_token`)
            user_id =payload_data['user_id'] #decode_token(token).get("user_id")
            if not user_id:
                raise Exception("Invalid or missing user_id in token")

            # Retrieve the last extension
            cursor.execute("SELECT id FROM ps_endpoints ORDER BY id DESC LIMIT 1")
            last_extension_row = cursor.fetchone()
            last_extension = int(last_extension_row['id']) if last_extension_row else 200003

            # Generate the new extension
            new_extension = last_extension + 1
            if new_extension > 299999:
                raise Exception("No more extensions available")

            # Generate a random password
            password = ''.join(random.choices(
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*',
                k=12
            ))

            # Static values
            static_values = {
                "transport": "transport-ws",
                "context": "testing",
                "disallow": "all",
                "allow": "opus,ulaw,alaw",
                "direct_media": "no",
                "auth_type": "userpass",
                "max_contacts": 1,
                "qualify_frequency": 30,
                "disable_direct_media_on_nat": "yes",
                "force_rport": "yes",
                "ice_support": "yes",
                "rewrite_contact": "yes",
                "rtp_symmetric": "yes",
                "use_avpf": "yes",
                "media_encryption": "sdes",
                "dtls_verify": "fingerprint",
                "dtls_rekey": "0",
                "dtls_cert_file": "/etc/letsencrypt/live/tcdev.site/fullchain.pem",
                "dtls_private_key": "/etc/letsencrypt/live/tcdev.site/privkey.pem",
                "dtls_setup": "actpass",
                "rtcp_mux": "yes",
                "webrtc": "yes",
                "is_selected": "1",
            }

            # Check if extension already exists
            cursor.execute("SELECT id FROM ps_endpoints WHERE id = %s", (new_extension,))
            if cursor.fetchone():
                raise Exception("Extension already exists")

            # Insert endpoint
            cursor.execute("""
                INSERT INTO ps_endpoints 
                (id, transport, aors, auth, context, disallow, allow, direct_media,
                 disable_direct_media_on_nat, force_rport, ice_support, rewrite_contact, 
                 rtp_symmetric, use_avpf, media_encryption, dtls_verify, dtls_rekey, 
                 dtls_cert_file, dtls_private_key, dtls_setup, rtcp_mux, webrtc, user_id,is_selected)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                new_extension,
                static_values["transport"],
                new_extension,
                new_extension,
                static_values["context"],
                static_values["disallow"],
                static_values["allow"],
                static_values["direct_media"],
                static_values["disable_direct_media_on_nat"],
                static_values["force_rport"],
                static_values["ice_support"],
                static_values["rewrite_contact"],
                static_values["rtp_symmetric"],
                static_values["use_avpf"],
                static_values["media_encryption"],
                static_values["dtls_verify"],
                static_values["dtls_rekey"],
                static_values["dtls_cert_file"],
                static_values["dtls_private_key"],
                static_values["dtls_setup"],
                static_values["rtcp_mux"],
                static_values["webrtc"],
                user_id,
                static_values["is_selected"],

            ))

            # Insert authentication
            cursor.execute("""
                INSERT INTO ps_auths 
                (id, auth_type, password, username)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                new_extension,
                static_values["auth_type"],
                password,
                new_extension
            ))

            # Insert AOR (Address of Record)
            cursor.execute("""
                INSERT INTO ps_aors 
                (id, max_contacts, qualify_frequency)
                VALUES (%s, %s, %s, %s)
            """, (
                new_extension,
                static_values["max_contacts"],
                static_values["qualify_frequency"]
            ))

            # Commit the transaction
            db.commit()

            # Return the new extension details
            return {
                "extension": new_extension,
                "password": password,
                "user_id": user_id
            }

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
                SELECT id, (SELECT password FROM  ps_auths pa WHERE pa.id = e.id) as password
                FROM ps_endpoints e
                WHERE e.user_id = %s AND e.is_selected=1 
                ORDER BY e.id
            """, (user_id,))
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Error fetching user extensions: {e}")
            return []
        finally:
            cursor.close()