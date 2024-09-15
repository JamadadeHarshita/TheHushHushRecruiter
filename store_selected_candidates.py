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

 