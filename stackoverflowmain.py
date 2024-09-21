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
    CREATE TABLE IF NOT EXISTS users (
        _id INTEGER PRIMARY KEY,
        display_name TEXT,
        reputation INTEGER,
        email TEXT,
        up_vote_count INTEGER,
        down_vote_count INTEGER,
        bronze_badges INTEGER,
        silver_badges INTEGER,
        gold_badges INTEGER
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
            INSERT OR REPLACE INTO users (ID, "Display Name", Reputation, Email, Upvotes,
        Downvotes ,Bronze, Silver, Gold)
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

 