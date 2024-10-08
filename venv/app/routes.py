from flask import render_template, redirect, url_for, request, flash
from flask_mail import Message
from sklearn.preprocessing import StandardScaler
from app import mail
from flask import session
import logging
import sqlite3
import uuid
import pickle
import pandas as pd
import random


# Load the model from the pkl file
with open('logreg_model_.pkl', 'rb') as model_file:
    logreg_model = pickle.load(model_file)


def fetch_users():
    conn = sqlite3.connect('stackoverflow_users.db')
    df = pd.read_sql_query("SELECT * FROM fetched", conn)
    conn.close()
    return df



# Function to make predictions
def predict_candidates(df):

    print(df.columns)


    # Select relevant features for prediction
    features = df[['Reputation', 'Upvotes', 'Bronze', 'Silver', 'Gold']]
    
    # Standardize the features
    sc = StandardScaler()
    scaled_features = sc.fit_transform(features)

    # Make predictions using the logistic regression model
    df['predicted_label'] = logreg_model.predict(scaled_features)

    # Get prediction probabilities (commented out if not needed)
    # df['probability_class_1'] = logreg_model.predict_proba(scaled_features)[:, 1]
    print(df['predicted_label'] == 1)

    # Filter the top candidates (assuming '1' is the positive class for top candidates)
    top_candidates = df[df['predicted_label'] == 1][['_id', 'display_name', 'Reputation', 'Upvotes', 'Bronze', 'Silver', 'Gold']]
  
    top_candidates = df[df['predicted_label'] == 1][[ '_id','display_name', 'Reputation', 'email', 'Upvotes', 'down_vote_count', 'Bronze','Silver', 'Gold' ]]
    # top_candidates = top_candidates.sort_values(by='Reputation', ascending=False)
    print(top_candidates[['_id','display_name', 'Reputation', 'email', 'Upvotes', 'down_vote_count', 'Bronze','Silver', 'Gold']])

    # Sort the candidates by the highest probability of being in class '1' (optional)
    # top_candidates = top_candidates.sort_values(by='probability_class_1', ascending=False)

    # Return the top candidates
    return top_candidates.head(5)


def get_or_create_uuid():
    if 'uuid' not in session:
        # Generate a new UUID
        session['uuid'] = str(uuid.uuid4())
    return session['uuid']


# Send the test link to eligible users via email
def send_test_link_email(username, recipient_email="jamadadeharshita@gmail.com"):
    msg = Message(
        subject="Coding Challenge Invitation",
        recipients=[recipient_email]
    )
    
    msg.body = f"""
        Hi {username},

        We hope this message finds you well. Based on a review of your Stackoverflow Profile, we would like to invite you to participate in a evaluation as part of our talent discovery process at Doodle.

        Please follow the link below to complete a short technical challenge:
        http://127.0.0.1:5000/test_link

        Your participation is confidential, and we will reach out with next steps if you're a good match for one of our upcoming opportunities.

        Best regards,
        The Doodle Recruitment Team
        """
    
    try:
        # Attempt to send the email
        mail.send(msg)
        logging.info(f"Test link email sent successfully to {recipient_email}")
        return f"Email successfully sent to {recipient_email}"
    
    except Exception as e:
        # Log the error and return failure message
        logging.error(f"Failed to send email to {recipient_email}: {e}")
        return f"Failed to send email to {recipient_email}. Error: {e}"



def send_confirmation_email(username):
    recipient_email = "jamadadeharshita@gmail.com" 

    msg = Message("Coding Challenge Submission Confirmation",
                  recipients=[recipient_email])

    msg.body = f"""
    Dear {username},

   Thank you for submitting your solution.

    Our team will review your submission and get back to you with feedback shortly.

    Best regards,
    Doodle Recruitment Team
    """

    # Send the email using Flask-Mail
    mail.send(msg)



def send_selection_email(username, feedback_text=None):
    recipient_email = "jamadadeharshita@gmail.com" 
    
    msg = Message("Congratulations! You've been selected",
                  recipients=[recipient_email])

    if feedback_text:
        msg.body = f"""
        Dear {username},

        Congratulations! Based on your submission, you have been selected.

        Feedback: {feedback_text}

        Best regards,
        Doodle Recruitment Team
        """
    else:
        msg.body = f"""
        Dear {username},

        Congratulations! Based on your submission, you have been selected.

        Best regards,
        Doodle Recruitment Team
        """

    # Send the email using Flask-Mail
    mail.send(msg)




def send_rejection_email(username, feedback_text=None):
    recipient_email = "jamadadeharshita@gmail.com"  # Use your email for testing
    
    msg = Message("Your Submission Result",
                  recipients=[recipient_email])

    if feedback_text:
        msg.body = f"""
        Dear {username},

        Thank you for your submission. Unfortunately, you have not been selected.

        Feedback: {feedback_text}

        Best regards,
        Doodle Recruitment Team
        """
    else:
        msg.body = f"""
        Dear {username},

        Thank you for your submission. Unfortunately, you have not been selected.

        Best regards,
        Doodle Recruitment Team
        """

    # Send the email using Flask-Mail
    mail.send(msg)




def register_routes(app):

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            # Fetch users from the database
            users_df = fetch_users()
            print("Fetching users...")

            # Use the ML model to predict top candidates
            top_candidates = predict_candidates(users_df)


            # Store the top candidates in the session
            session['usernames'] = top_candidates['display_name'].tolist()

                    # Store top candidates in the 'selected_candidates' table
            try:
                conn = sqlite3.connect('stackoverflow_users.db')
                c = conn.cursor()

                # Create the table if it doesn't exist
                c.execute('''
                    CREATE TABLE IF NOT EXISTS topselected_candidates (
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

                # Insert top candidates into the table
                for index, row in top_candidates.iterrows():
                    c.execute('''
                        INSERT INTO topselected_candidates (ID,Display_Name, Reputation, Email, Upvotes, Downvotes, Bronze, Silver, Gold, ylabel)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (row['_id'], row['display_name'], row['Reputation'], row['email'], row['Upvotes'], row['down_vote_count'], row['Bronze'], row['Silver'], row['Gold'], 1))  # Assuming ylabel is 1 for top candidates

                conn.commit()
                conn.close()
                print("Top candidates stored successfully.")

            except Exception as e:
                    print(f"An error occurred while storing top candidates: {e}")

            # Notify the top candidates
            for index, row in top_candidates.iterrows():
                send_test_link_email(row['display_name'], 'jamadadeharshita@gmail.com')

                   # Flash a success message to display in the popup
            flash('Emails have been successfully sent to the top candidates.')

            # Return the top candidates to the UI
            return render_template('top_candidates.html', candidates=top_candidates.to_dict(orient='records'))

        return render_template('index.html')


    @app.route('/top_candidates')
    def top_candidates():
        return render_template('top_candidates.html')

    @app.route('/test_link')
    def test_link():
        challenges = [
            "Problem Statement: You are given a list of meeting time intervals. Write a function to find the minimum number of meeting rooms required. Intervals may overlap. Example: Input: [(0, 30), (5, 10), (15, 20)] → Output: 2",
            "Problem Statement: Given an unsorted array of integers, write a function to find the length of the longest consecutive sequence of numbers. Your algorithm should run in *O(n)* time.  Example: Input: [100, 4, 200, 1, 3, 2] → Output: 4 (sequence: 1, 2, 3, 4).",
            "Problem Statement: Given two strings, write a function that checks if one string is a circular shift of the other. A circular shift means the string can be rotated any number of places and still match the other string. Example: Input: ('abcde', 'cdeab') → Output: True, Input: ('abc', 'acb') → Output: False"
        ]
        selected_challenge = random.choice(challenges)    
        # Store the selected challenge in the session
        session['challenge'] = selected_challenge
        return render_template('coding_challenge.html', challenge=selected_challenge)



    @app.route('/submit_code', methods=['POST'])
    def submit_code():
        try:
            # Get the user's input
            code = request.form.get('code')
            entered_username = request.form.get('username')  # Get the username from the user input
            
            # Retrieve the challenge from the session
            challenge = session.get('challenge')

            # Error: No code submitted
            if not code:
                return render_template('coding_challenge.html', error="No code submitted. Please enter your code.", challenge=challenge)
            
            # Error: No username entered
            if not entered_username:
                return render_template('coding_challenge.html', error="No username entered. Please provide your username.", challenge=challenge)
            
            # Connect to the SQLite database
            conn = sqlite3.connect('stackoverflow_users.db')
            c = conn.cursor()

            # Check if the entered username exists in the selected_candidates table
            c.execute('''
                SELECT * FROM topselected_candidates WHERE "Display_Name" = ?
            ''', (entered_username,))
            
            candidate = c.fetchone()

            # If the candidate is not found, return an error and keep displaying the challenge
            if not candidate:
                conn.close()
                return render_template('coding_challenge.html', error="You are not an eligible candidate. Please check your username.", challenge=challenge)
            
            # If the candidate exists, proceed to get the user ID
            user_id = candidate[0]

            # Check if the user has already submitted a solution
            c.execute('''
                SELECT * FROM submissions_1 WHERE id = ?
            ''', (user_id,))
            
            existing_submission = c.fetchone()

            if existing_submission:
                conn.close()
                # If a submission already exists, display a message that they've already submitted their code
                return render_template('coding_challenge.html', error="You've already submitted your solution.", challenge=challenge)
            
            # Insert the submitted code and user's ID into the 'submissions_1' table
            c.execute('''
                INSERT INTO submissions_1 (id, username, code) 
                VALUES (?, ?, ?)
            ''', (user_id, entered_username, code))

            # Commit changes and close the database connection
            conn.commit()
            conn.close()

            # Send a confirmation email to the user after submission
            send_confirmation_email(entered_username)

            # Render a confirmation template
            return render_template('submission_confirmation.html')

        except Exception as e:
            print("An error occurred:", e)
            challenge = session.get('challenge')
            return render_template('coding_challenge.html', error="An internal error occurred. Please try again.", challenge=challenge)




    @app.route('/evaluation')
    def evaluation():
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect('stackoverflow_users.db')
            c = conn.cursor()

            # Fetch all submissions from the 'submissions_1' table
            c.execute("SELECT id, username, code, submission_time FROM submissions_1")
            submissions = c.fetchall()

            conn.close()

            # Check if there are any submissions
            if not submissions:
                return render_template('error.html', message="No submissions found.")

            # Pass the submissions to the evaluation.html template
            return render_template('evaluation.html', submissions=submissions)

        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('error.html', message="An internal error occurred. Please try again.")


    @app.route('/manager')
    def manager_dashboard():
        conn = sqlite3.connect('stackoverflow_users.db')
        c = conn.cursor()

        # Fetch submissions data without code
        c.execute("SELECT id, username, submission_time FROM submissions_1")
        submissions = c.fetchall()
        conn.close()

        return render_template('manager.html', submissions=submissions)

    @app.route('/feedback/<submission_id>', methods=['GET', 'POST'])
    def feedback(submission_id):
        conn = sqlite3.connect('stackoverflow_users.db')
        c = conn.cursor()

        # Fetch the submission details based on submission_id
        c.execute('SELECT id, username, code, feedback, score FROM submissions_1 WHERE id = ?', (submission_id,))
        submission_data = c.fetchone()

        if not submission_data:
            return render_template('error.html', message="Submission not found.")

        user_id, username, code, feedback, score = submission_data

        if request.method == 'POST':
            # Get feedback and score from the form
            feedback_text = request.form.get('feedback')
            # score = request.form.get('score', None)

            # Determine if the manager selected the candidate or not
            action = request.form.get('action')

            if action == 'selected':
                # Send an email for selection
                send_selection_email(username, feedback_text)
                selection_status = "Selected"
            elif action == 'not_selected':
                # Send an email for rejection
                send_rejection_email(username, feedback_text)
                selection_status = "Not Selected"

            # Update the feedback and score for the specific submission
            c.execute('''
                UPDATE submissions_1
                SET feedback = ?, score = ?, selection_status = ?
                WHERE id = ?
            ''', (feedback_text, score, selection_status, submission_id))

            conn.commit()
            conn.close()

            return redirect(url_for('index'))

        return render_template('feedback.html', submission_id=submission_id, user_id=user_id, username=username, code=code, feedback=feedback, score=score)


    @app.route('/submission_confirmation')
    def submission_confirmation():
        email = "jamadadeharshita@gmail.com"  
        return render_template('submission_confirmation.html', email=email)
    
    

    