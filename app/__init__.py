from flask import Flask
import mysql.connector
from config import Config

db = None

def get_db():
    global db
    if not db:
        db = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
    return db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.routes.api import api
    app.register_blueprint(api, url_prefix='/api')

    return app
