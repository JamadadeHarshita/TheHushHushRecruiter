import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=2)


    # Flask-Mail Configuration for Gmail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'engineerdata061@gmail.com'
    MAIL_PASSWORD = "cmgn nmds wkig lvfo"  
    MAIL_DEFAULT_SENDER = 'engineerdata061@gmail.com' 



#cmgn nmds wkig lvfo