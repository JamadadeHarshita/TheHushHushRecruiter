from flask import Flask
from flask_mail import Mail
from config import Config
import sqlite3

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mail.init_app(app)
    
    from app import routes 
    
    return app


import requests
import time
import re
import sqlite3


# Function to fetch user data from the Stack Exchange API
def fetch_stack_overflow_data(page):
    base_url = f'https://api.stackexchange.com/2.3/users'
    params = {
        'page': page,
        'pagesize': 100,
        'order': 'desc',
        'sort': 'modified',
        'site': 'stackoverflow',
        'filter': '!.nCWISkNpIcXxHxPbpvKfsz8d4B2KVduPczTmaD5QjF475r'
    }
    response = requests.get(base_url, params=params)
    return response.json()

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('stackoverflow_users.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS fetched (
        _id INTEGER PRIMARY KEY,
        display_name TEXT,
        Reputation INTEGER,
        email TEXT,
        Upvotes INTEGER,
        down_vote_count INTEGER,
        Bronze INTEGER,
        Silver INTEGER,
        Gold INTEGER

    )
''')

# Initialize a list to save user records
user_records = []
print("hello")

# Fetch data until page 10
for page_number in range(1, 5):
    # Print status
    print(f"Requesting page {page_number}/10")

    # Get Data
    response_data = fetch_stack_overflow_data(page_number)

    # Save the users
    for user in response_data['items']:
        user['_id'] = user.pop('user_id')
        # Clean up display name and create email
        email_name = re.sub(r'[^a-zA-Z0-9]', '', user['display_name'])
        user['email'] = email_name.lower() + '@gmail.com'  # Set email format to displayname@gmail.com

        # Insert data into the SQLite database
        c.execute('''
            INSERT OR REPLACE INTO fetched (_id, display_name, Reputation, email, Upvotes, down_vote_count, Bronze, Silver, Gold)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user['_id'], 
            user['display_name'], 
            user.get('reputation', 0), 
            user['email'],
            user.get('up_vote_count', 0),  
            user.get('down_vote_count', 0), 
            user.get('badge_counts', {}).get('bronze', 0), 
            user.get('badge_counts', {}).get('silver', 0), 
            user.get('badge_counts', {}).get('gold', 0)  # Insert gold badges value
        ))

    # Commit changes to the database after each page
    conn.commit()

    # If the result is not in cache, sleep to avoid throttling
    if response_data.get('has_more', False):
        time.sleep(11)
    else:
        break

# Close the database connection
conn.close()
print(f"Data saved to SQLite database 'stackoverflow_users.db'")

 

 

def create_submissions_table():
    conn = sqlite3.connect('stackoverflow_users.db')
    c = conn.cursor()

    # Create table if it doesn't exist, without AUTO INCREMENT
    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions_1 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing ID for submissions
            user_id TEXT,  -- Store the UUID here
            username TEXT NOT NULL,
            code TEXT NOT NULL,
            submission_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Call this function to initialize or update the database
create_submissions_table()

def add_feedback_columns():
    conn = sqlite3.connect('stackoverflow_users.db')
    c = conn.cursor()

    # Add 'feedback' and 'score' columns if they don't already exist
    try:
        c.execute("ALTER TABLE submissions_1 ADD COLUMN feedback TEXT;")
    except sqlite3.OperationalError:
        # If the column already exists, skip the operation
        print("The 'feedback' column already exists.")

    try:
        c.execute("ALTER TABLE submissions_1 ADD COLUMN score INTEGER;")
    except sqlite3.OperationalError:
        # If the column already exists, skip the operation
        print("The 'score' column already exists.")

    conn.commit()
    conn.close()

# Call this function to ensure columns are present
add_feedback_columns()















