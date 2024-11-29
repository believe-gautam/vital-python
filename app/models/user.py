from app import get_db
import bcrypt
import jwt
from datetime import datetime, timedelta
from config import Config
import mysql.connector
import random
import string 


class User:
    @staticmethod
    def create(mobile_number, password):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Hash the password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        try:
            cursor.execute(
                'INSERT INTO users (mobile_number, password) VALUES (%s, %s)',
                (mobile_number, hashed)
            )
            db.commit()
            return True
        except mysql.connector.IntegrityError:
            return False
        finally:
            cursor.close()
    
    @staticmethod
    def authenticate(mobile_number, password):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE mobile_number = %s', (mobile_number,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return user
        return None
    
    @staticmethod
    def generate_token(user_id):
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    
    
    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()
        return user

    @staticmethod
    def get_all_users():
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        cursor.close()
        return users
    

    @staticmethod
    def generate_otp(mobile_number):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        otp = ''.join(random.choices(string.digits, k=6))
        
        expiration = datetime.utcnow() + timedelta(minutes=15)
        
        try:
            cursor.execute('''
                UPDATE users 
                SET otp = %s, 
                    otp_expiration = %s, 
                    is_otp_verified = %s
                WHERE mobile_number = %s
            ''', (otp, expiration, False, mobile_number))
            
            db.commit()
            
            cursor.execute('SELECT * FROM users WHERE mobile_number = %s', (mobile_number,))
            user = cursor.fetchone()
            
            return otp if user else None
        except Exception as e:
            print(f"OTP generation error: {e}")
            return None
        finally:
            cursor.close()

    @staticmethod
    def verify_otp(mobile_number, otp):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT * FROM users 
                WHERE mobile_number = %s 
                AND otp = %s 
                AND otp_expiration > %s 
                AND is_otp_verified = %s
            ''', (mobile_number, otp, datetime.utcnow(), False))
            
            user = cursor.fetchone()
            
            if user:
                cursor.execute('''
                    UPDATE users 
                    SET is_otp_verified = %s 
                    WHERE mobile_number = %s
                ''', (True, mobile_number))
                db.commit()
                return True
            return False
        finally:
            cursor.close()

    @staticmethod
    def reset_password_with_otp(mobile_number, new_password):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT * FROM users 
                WHERE mobile_number = %s 
                AND is_otp_verified = %s
            ''', (mobile_number, True))
            
            user = cursor.fetchone()
            
            if not user:
                return False
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                UPDATE users 
                SET password = %s, 
                    otp = NULL, 
                    otp_expiration = NULL, 
                    is_otp_verified = %s
                WHERE mobile_number = %s
            ''', (hashed, False, mobile_number))
            
            db.commit()
            return True
        except Exception as e:
            print(f"Password reset error: {e}")
            return False
        finally:
            cursor.close()

    @staticmethod
    def send_otp_to_mobile(mobile_number):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT * FROM users WHERE mobile_number = %s', (mobile_number,))
            user = cursor.fetchone()
            
            if not user:
                return None
            otp = User.generate_otp(mobile_number)
            print(f"OTP {otp} sent to mobile number {mobile_number}")
            
            return otp
        except Exception as e:
            print(f"Error sending OTP: {e}")
            return None
        finally:
            cursor.close()