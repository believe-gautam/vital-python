from app import get_db

def init_db():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255),
            otp VARCHAR(6),
            otp_expiration DATETIME,
            is_otp_verified BOOLEAN DEFAULT FALSE,
            reset_token VARCHAR(255),
            reset_token_expiration DATETIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    db.commit()
    cursor.close()
