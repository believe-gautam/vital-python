# config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'phpadmin')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'dsahjkdash98732893@Tc2929')
    MYSQL_DB = os.getenv('MYSQL_DB', 'asterisk')

    # SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    # MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    # MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    # MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    # MYSQL_DB = os.getenv('MYSQL_DB', 'asterisk')
