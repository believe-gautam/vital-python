from app import get_db
import bcrypt
import jwt
from datetime import datetime, timedelta
from config import Config

class User:
    @staticmethod
    def create(username, email, password):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Hash the password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        try:
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                (username, email, hashed)
            )
            db.commit()
            return True
        except mysql.connector.IntegrityError:
            return False
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