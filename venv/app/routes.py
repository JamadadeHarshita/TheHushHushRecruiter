from flask import render_template, redirect, url_for, request, flash
from app.models import Submission, Feedback, db  # Assuming you have these models
from app.forms import UsernameForm
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

from store_selected_candidates import store_top_candidates
# from stack_main_ML import fetch_users_to_dataframe
from store_selected_candidates import get_top_candidates



# Load the KMeans model from the pkl file
with open('logreg_models.pkl', 'rb') as model_file:
    logreg_model = pickle.load(model_file)


def fetch_users():
    conn = sqlite3.connect('stackoverflow_users.db')
    df = pd.read_sql_query("SELECT * FROM fetched", conn)
    conn.close()
    return df



# Function to make predictions
def predict_candidates(df):
    # Ensure the DataFrame contains relevant columns
    
    # df.rename(columns={
    #     'reputation': 'Reputation',
    #     'up_vote_count': 'Upvotes',
    #     'bronze_badges': 'Bronze',
    #     'silver_badges': 'Silver',
    #     'gold_badges': 'Gold'
    # }, inplace=True)

    print(df.columns)


    # Select relevant features for prediction
    features = df[['Reputation', 'Upvotes', 'Bronze', 'Silver', 'Gold']]
    
    # Standardize the features
    # sc = StandardScaler()
    # scaled_features = sc.fit_transform(features)

    # Make predictions using the logistic regression model
    df['predicted_label'] = logreg_model.predict(features)

    # Get prediction probabilities (commented out if not needed)
    # df['probability_class_1'] = logreg_model.predict_proba(scaled_features)[:, 1]
    print(df['predicted_label'] == 1)

    # Filter the top candidates (assuming '1' is the positive class for top candidates)
    # top_candidates = df[df['predicted_label'] == 1][['_id', 'display_name', 'Reputation', 'Upvotes', 'Bronze', 'Silver', 'Gold']]
  
    top_candidates = df[df['predicted_label'] == 1][[ '_id','display_name', 'Reputation', 'email', 'Upvotes', 'down_vote_count', 'Bronze','Silver', 'Gold' ]]
    top_candidates = top_candidates.sort_values(by='Reputation', ascending=False)
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

    Congratulations! Based on your profile, you're invited to participate in a coding test.

    Please use this link to take the test: http://127.0.0.1:5000/test_link

    Best regards,
    Doodle Recruitment Team
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
    recipient_email = "jamadadeharshita@gmail.com"  # Replace with the candidate's email (if available)

    msg = Message("Coding Challenge Submission Confirmation",
                  recipients=[recipient_email])

    msg.body = f"""
    Dear {username},

    We have received your coding challenge submission. Thank you for submitting your solution.

    Our team will review your submission and get back to you with feedback shortly.

    Best regards,
    Doodle Recruitment Team
    """

    # Send the email using Flask-Mail
    mail.send(msg)



# Send feedback emails to candidates
def send_feedback_email(username, feedback_text=None, score=None):
    recipient_email = "jamadadeharshita@gmail.com"  # Use your email for testing
    
    msg = Message("Feedback for Your Submission",
                  recipients=[recipient_email])

    if not feedback_text or feedback_text.strip() == "":
        msg.body = f"""
        Dear {username},

        Your submission has been reviewed. Unfortunately, no specific feedback was provided.

        Best regards,
        Doodle Recruitment Team
        """
    else:
        msg.body = f"""
        Dear {username},

        Your submission has been reviewed.

        Feedback: {feedback_text}
        Score: {score if score else 'N/A'}

        Best regards,
        Doodle Recruitment Team
        """

    # Send the email using Flask-Mail
    mail.send(msg)


def register_routes(app):
    # @app.route('/', methods=['GET', 'POST'])
    # def index():
    #     form = UsernameForm()

    #     # Check if the button to run the ML model is clicked
    #     if request.method == 'POST':
    #         # Run the machine learning model and store the top candidates
    #         store_top_candidates()

    #         # Fetch the top 5 candidates
    #         top_candidates = get_top_candidates()

    #         # Send email to the top candidates
    #         for index, row in top_candidates.iterrows():
    #             send_test_link_email(row['Display Name'], 'alistairpereira241999@gmail.com')

    #         # Flash message to notify that top candidates have been selected
    #         flash("Top candidates have been selected and emailed successfully.")

    #         # Save top candidates' username in session
    #         session['usernames'] = [row['Display Name'] for index, row in top_candidates.iterrows()]
            
    #         flash("Top candidates have been selected. Their usernames are stored in the session.")
    #         return render_template('top_candidates.html', candidates=top_candidates.to_dict(orient='records'))

    #     return render_template('index.html', form=form)


    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            # Fetch users from the database
            users_df = fetch_users()
            print("Fetching users...")

            print("blabla")
            # Use the ML model to predict top candidates
            top_candidates = predict_candidates(users_df)
            print("god")

                    # Use the ML model to predict top candidates


            # Store the top candidates in the session
            session['usernames'] = top_candidates['display_name'].tolist()

            # Notify the top candidates
            for index, row in top_candidates.iterrows():
                send_test_link_email(row['display_name'], 'jamadadeharshita@gmail.com')

            # Return the top candidates to the UI
            return render_template('top_candidates.html', candidates=top_candidates.to_dict(orient='records'))

        return render_template('index.html')


    

    @app.route('/top_candidates')
    def top_candidates():
        return render_template('top_candidates.html')

    @app.route('/test_link')
    def test_link():
        challenges = [
            "Challenge 1: Write a function to reverse a string.",
            "Challenge 2: Write a function to find the sum of an array.",
            "Challenge 3: Write a function to check if a number is prime."
        ]

        selected_challenge = random.choice(challenges)
        
        # Store the selected challenge in the session
        session['challenge'] = selected_challenge

        return render_template('coding_challenge.html', challenge=selected_challenge)


    # @app.route('/submit_code', methods=['POST'])
    # def submit_code():
    #     try:
    #         code = request.form.get('code')
            
    #         if not code:
    #             return render_template('coding_challenge.html', error="No code submitted. Please enter your code.")
            
    #                 # Automatically get the username from the session
    #         username = session.get('username', 'unknown_user')  # Default to 'unknown_user' if not set
            
            
    #         conn = sqlite3.connect('stackoverflow_users.db')
    #         c = conn.cursor()

    #                     # Get the user ID and username (you can modify this to fetch from the session or database)
    #         user_id = get_or_create_uuid()


    #         # Insert the submitted code and user's ID into the 'submissions' table
    #         c.execute('''
    #             INSERT INTO submissions_1 (id, username, code) 
    #             VALUES (?, ?, ?)
    #         ''', (user_id, username, code))

    #         conn.commit()
    #         conn.close()
    #                 # Send a confirmation email to the user after submission
    #         send_confirmation_email(username)

    #         return render_template('solution_confirmation.html')  # Create this template for confirmation
            

    #     except Exception as e:
    #         print("An error occurred:", e)
    #         return render_template('coding_challenge.html', error="An internal error occurred. Please try again.")

    @app.route('/submit_code', methods=['POST'])
    def submit_code():
        try:
            code = request.form.get('code')
            entered_username = request.form.get('username')  # Get the username from the user input
            
            if not code:
                return render_template('coding_challenge.html', error="No code submitted. Please enter your code.")
            
            if not entered_username:
                return render_template('coding_challenge.html', error="No username entered. Please provide your username.")
            
            conn = sqlite3.connect('stackoverflow_users.db')
            c = conn.cursor()

            # Check if the entered username exists in the selected_candidates table
            c.execute('''
                SELECT * FROM selected_candidates WHERE "Display Name" = ?
            ''', (entered_username,))
            
            candidate = c.fetchone()

            if not candidate:
                # If no candidate found with the entered username, show an error
                conn.close()
                return render_template('coding_challenge.html', error="You are not an eligible candidate. Please check your username.")
            
            # If the candidate exists, proceed to get the user ID and insert the submission
            user_id = candidate[0]  # Assuming the first column is the user ID
            
            # Insert the submitted code and user's ID into the 'submissions_1' table
            c.execute('''
                INSERT INTO submissions_1 (id, username, code) 
                VALUES (?, ?, ?)
            ''', (user_id, entered_username, code))

            conn.commit()
            conn.close()

            # Send a confirmation email to the user after submission
            send_confirmation_email(entered_username)

            return render_template('solution_confirmation.html')  # Create this template for confirmation

        except Exception as e:
            print("An error occurred:", e)
            return render_template('coding_challenge.html', error="An internal error occurred. Please try again.")


    # @app.route('/evaluation')
    # def evaluation():
    #     submissions = Submission.query.all()
    #     return render_template('evaluation.html', submissions=submissions)




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


    # Add the feedback route here
    # @app.route('/feedback/<int:submission_id>', methods=['GET', 'POST'])
    # def feedback(submission_id):
    #     submission = Submission.query.get_or_404(submission_id)

    #     if request.method == 'POST':
    #         feedback_text = request.form.get('feedback')
    #         score = int(request.form.get('score'))

    #         feedback = Feedback(submission_id=submission.id, feedback_text=feedback_text, score=score)
    #         db.session.add(feedback)
    #         db.session.commit()

    #         # Send feedback email
    #         send_feedback_email(submission.username, feedback_text, score)

    #         print(f"Feedback submitted for submission {submission_id}: {feedback_text} with score {score}")

    #         return redirect(url_for('evaluation'))

    #     return render_template('feedback.html', submission=submission)


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
            feedback_text = request.form.get('feedback')
            score = int(request.form.get('score'))

            # Update the feedback and score for the specific submission
            c.execute('''
                UPDATE submissions_1
                SET feedback = ?, score = ?
                WHERE id = ?
            ''', (feedback_text, score, submission_id))

            conn.commit()
            conn.close()

            # Send feedback email to the user
            send_feedback_email(username, feedback_text, score)

            return redirect(url_for('evaluation'))

        return render_template('feedback.html', submission_id=submission_id, user_id=user_id, username=username, code=code, feedback=feedback, score=score)
    # def feedback(submission_id):
    #     conn = sqlite3.connect('stackoverflow_users.db')
    #     c = conn.cursor()

    #     # Fetch the submission details based on submission_id
    #     c.execute('SELECT id, username, code FROM submissions_1 WHERE id = ?', (submission_id,))
    #     submission_data = c.fetchone()

    #     if not submission_data:
    #         return render_template('error.html', message="Submission not found.")

    #     user_id, username, code = submission_data

    #     if request.method == 'POST':
    #         feedback_text = request.form.get('feedback')
    #         score = int(request.form.get('score'))

    #         # Insert feedback linked to the submission_id
    #         c.execute('''
    #             INSERT INTO feedback (submission_id, feedback_text, score)
    #             VALUES (?, ?, ?)
    #         ''', (submission_id, feedback_text, score))

    #         conn.commit()
    #         conn.close()

    #         send_feedback_email(username, feedback_text, score)

    #         return redirect(url_for('evaluation'))

    #     return render_template('feedback.html', submission_id=submission_id, user_id=user_id, username=username, code=code)


        
    @app.route('/submission_confirmation')
    def submission_confirmation():
        email = "jamadadeharshita@gmail.com"  # Change this to dynamically use the user's email if needed
        return render_template('submission_confirmation.html', email=email)
    
    

    


# Dummy eligibility check function with hardcoded users
def check_eligibility(github_username, stackoverflow_username):
    eligible_users = ["eligible_user", "test_candidate"]  # Hardcoded eligible users
    
    # Check if either username is in the eligible users list
    if github_username in eligible_users or stackoverflow_username in eligible_users:
        return True, "You are eligible! Proceed to the coding challenge."
    
    return False, "Sorry, you are not eligible based on the provided information."

    