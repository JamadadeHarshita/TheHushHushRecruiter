# # config.py
# import os
# basedir = os.path.abspath(os.path.dirname(__file__))

import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///hushHushRecruiter.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=1)


    # Flask-Mail Configuration for Gmail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'engineerdata061@gmail.com'
    MAIL_PASSWORD = "cmgn nmds wkig lvfo"  # If using App Password, paste it here
    MAIL_DEFAULT_SENDER = 'engineerdata061@gmail.com'  # Same as your Gmail address



#cmgn nmds wkig lvfo