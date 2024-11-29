from app import get_db

def init_db():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
           id INT AUTO_INCREMENT PRIMARY KEY,
            mobile_number VARCHAR(15) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            otp VARCHAR(6) NULL,
            otp_expiration DATETIME NULL,
            is_otp_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    
    db.commit()
    cursor.close()