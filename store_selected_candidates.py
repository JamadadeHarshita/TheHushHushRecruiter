import sqlite3
import pandas as pd

# Function to fetch the top 5 candidates from the existing DataFrame
def get_top_candidates():
    # Connect to the database and fetch data
    # select all data from the database.
    conn = sqlite3.connect('stackoverflow_users.db')
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()

    #filter the data to get top_5_candidates
    df['ylabel'] = df['ylabel']  
    top_candidates = df[df['ylabel'] == 1]
    top_candidates = top_candidates.sort_values(by='Reputation', ascending=False)
    top_5_candidates = top_candidates.head(5)

    return top_5_candidates

#storing the top 5 candidates into a new table in SQLite
def store_top_candidates():
    top_candidates = get_top_candidates()

    conn = sqlite3.connect('stackoverflow_users.db')
    c = conn.cursor()

    # Create new table for selected candidates
    c.execute('''
        CREATE TABLE IF NOT EXISTS selected_candidates (
            ID INTEGER PRIMARY KEY,
            Display_Name TEXT,
            Reputation INTEGER,
            Email TEXT,
            Upvotes INTEGER,
            Downvotes INTEGER,
            Bronze INTEGER,
            Silver INTEGER,
            Gold INTEGER,
            ylabel INTEGER
        )
    ''')

    # Insert top 5 candidates into the new table
    top_candidates.to_sql('selected_candidates', conn, if_exists='replace', index=False)

    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Top 5 candidates have been stored in the 'selected_candidates' table.")

if __name__ == "__main__":
    store_top_candidates()



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
    CREATE TABLE IF NOT EXISTS dummyusers (
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
            INSERT OR REPLACE INTO dummyusers (_id, display_name, reputation, email, up_vote_count,
        down_vote_count , bronze_badges, silver_badges, gold_badges)
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

 

 