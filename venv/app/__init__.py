from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from config import Config
import sqlite3

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    from app import routes 
    
    return app

def create_submissions_table():
    conn = sqlite3.connect('stackoverflow_users.db')
    c = conn.cursor()

    # Create table if it doesn't exist, without AUTO INCREMENT
    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY,  -- ID will be provided manually (user's ID)
            username TEXT NOT NULL,
            code TEXT NOT NULL,
            submission_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Call this function to initialize or update the database
create_submissions_table()














