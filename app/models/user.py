from app import get_db
import bcrypt
import jwt
from datetime import datetime, timedelta
from config import Config
import mysql.connector
import random
import string 
import os

class User:
    @staticmethod
    def create_user(username, email, otp):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        expiration = datetime.utcnow() + timedelta(minutes=15)  

        try:
            cursor.execute(''' 
                INSERT INTO users (username, email, otp, otp_expiration, is_otp_verified) 
                VALUES (%s, %s, %s, %s, %s)
            ''', (username, email, otp, expiration, False))
            db.commit()
            return True
        except mysql.connector.IntegrityError:
            return False
        finally:
            cursor.close()

    @staticmethod
    def verify_otp(email, otp):
        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute('''
                SELECT * FROM users 
                WHERE email = %s AND otp = %s AND otp_expiration > %s
            ''', (email, otp, datetime.utcnow()))

            user = cursor.fetchone()
            if user:
                cursor.execute('''
                    UPDATE users 
                    SET is_otp_verified = %s,
                        otp = ''
                    WHERE email = %s
                ''', (True, email))
                db.commit()
                return {"status": True,"user_data":user}
            return {"status": False,"user_data":{}}
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
        finally:
            cursor.close()

    @staticmethod
    def set_password(email, new_password):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        try:
            cursor.execute('''
                UPDATE users 
                SET password = %s, otp = NULL, otp_expiration = NULL, is_otp_verified = %s
                WHERE email = %s AND is_otp_verified = %s
            ''', (hashed, False, email, True))  
            db.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()

    @staticmethod
    def authenticate(email, password):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return user
        return None

    @staticmethod
    def generate_token(user_id):
        # payload = {
        #     'user_data': user_id,
        #     'exp': datetime.utcnow() + timedelta(days=1)
        # }
        # return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

        try:
            # Token payload
            payload = {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(days=1),  # Token expires in 1 day
                'iat': datetime.utcnow()
            }
            # Generate token
            token = jwt.encode(
                payload,
                os.getenv('JWT_SECRET_KEY'),
                algorithm="HS256"
            )
            return token
        except Exception as e:
            print(e)
            return None



    @staticmethod
    def generate_reset_token(email):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Generate a random token
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        expiration = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour

        try:
            cursor.execute('''
                UPDATE users 
                SET reset_token = %s, reset_token_expiration = %s 
                WHERE email = %s
            ''', (token, expiration, email))
            db.commit()
            return token
        finally:
            cursor.close()

    @staticmethod
    def verify_reset_token(token):
        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute('''
                SELECT * FROM users 
                WHERE reset_token = %s AND reset_token_expiration > %s
            ''', (token, datetime.utcnow()))
            user = cursor.fetchone()
            return user
        finally:
            cursor.close()

    @staticmethod
    def reset_password(token, new_password):
        db = get_db()
        cursor = db.cursor(dictionary=True)

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        try:
            cursor.execute('''
                UPDATE users 
                SET password = %s, reset_token = NULL, reset_token_expiration = NULL 
                WHERE reset_token = %s
            ''', (hashed_password, token))
            db.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()

    @staticmethod
    def get_user_by_email(email):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        return user

    @staticmethod
    def get_by_id(user_id):
        cursor = None
        try:
            print("Attempting to find user with ID:", user_id)
            db = get_db()
            cursor = db.cursor(dictionary=True)
            
            # The query we'll execute
            query = '''SELECT * FROM users WHERE id = %s'''
            print("Query template:", query)
            print("Parameters:", (user_id,))
            
            # Execute the query
            cursor.execute(query, (user_id,))
            
            # Fetch the result after executing
            find_user = cursor.fetchone()
            print("Query result:", find_user)
            
            db.commit()
            return find_user
            
        except Exception as e:
            print("Database error occurred:")
            print("Error message:", str(e))
            print("Error type:", type(e).__name__)
            # You might want to log the error here
            
            # Optionally, re-raise the exception if you want it to propagate
            raise e
        
        finally:
            # Make sure to close the cursor
            if cursor:
                cursor.close()
                
    @staticmethod
    def get_by_email(cls, email):
        query = "SELECT * FROM users WHERE email = %s"
        return cls.execute_single(query, (email,))

    def generate_token2(self, user_id):
        try:
            # Token payload
            payload = {
                'user_data': user_id,
                'exp': datetime.utcnow() + timedelta(days=1),  # Token expires in 1 day
                'iat': datetime.utcnow()
            }
            # Generate token
            token = jwt.encode(
                payload,
                os.getenv('JWT_SECRET_KEY'),
                algorithm="HS256"
            )
            return token
        except Exception as e:
            return None