from flask import render_template, redirect, url_for, request, flash
from app.models import Submission, Feedback, db  # Assuming you have these models
from app.forms import UsernameForm
from flask_mail import Message
from app import mail
from flask import session
import logging

import random

from store_selected_candidates import store_top_candidates
from stack_main_ML import fetch_users_to_dataframe
from store_selected_candidates import get_top_candidates


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
    @app.route('/', methods=['GET', 'POST'])
    def index():
        form = UsernameForm()

        # Check if the button to run the ML model is clicked
        if request.method == 'POST':
            # Run the machine learning model and store the top candidates
            store_top_candidates()

            # Fetch the top 5 candidates
            top_candidates = get_top_candidates()

            # Send email to the top candidates
            for index, row in top_candidates.iterrows():
                send_test_link_email(row['Display Name'], 'jamadadeharshita@gmail.com')

            # Flash message to notify that top candidates have been selected
            flash("Top candidates have been selected and emailed successfully.")
            return render_template('top_candidates.html', candidates=top_candidates.to_dict(orient='records'))

        return render_template('index.html', form=form)

    

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


    @app.route('/submit_code', methods=['POST'])
    def submit_code():
        try:
            code = request.form.get('code')
            username = "mock_user"  # Replace with actual logic to get the username
            if not code:
                return render_template('coding_challenge.html', error="No code submitted. Please enter your code.")
            
            submission = Submission(username=username, code=code)
            db.session.add(submission)
            db.session.commit()

                    # Send a confirmation email to the user after submission
            send_confirmation_email(username)

            return render_template('solution_confirmation.html')  # Create this template for confirmation
            
            return redirect(url_for('evaluation'))
        except Exception as e:
            print("An error occurred:", e)
            return render_template('coding_challenge.html', error="An internal error occurred. Please try again.")

    @app.route('/evaluation')
    def evaluation():
        submissions = Submission.query.all()
        return render_template('evaluation.html', submissions=submissions)

    # Add the feedback route here
    @app.route('/feedback/<int:submission_id>', methods=['GET', 'POST'])
    def feedback(submission_id):
        submission = Submission.query.get_or_404(submission_id)

        if request.method == 'POST':
            feedback_text = request.form.get('feedback')
            score = int(request.form.get('score'))

            feedback = Feedback(submission_id=submission.id, feedback_text=feedback_text, score=score)
            db.session.add(feedback)
            db.session.commit()

            # Send feedback email
            send_feedback_email(submission.username, feedback_text, score)

            print(f"Feedback submitted for submission {submission_id}: {feedback_text} with score {score}")

            return redirect(url_for('evaluation'))

        return render_template('feedback.html', submission=submission)
    
    @app.route('/submission_confirmation')
    def submission_confirmation():
        email = "engineerdata061@gmail.com"  # Change this to dynamically use the user's email if needed
        return render_template('submission_confirmation.html', email=email)
    
    

    


# Dummy eligibility check function with hardcoded users
def check_eligibility(github_username, stackoverflow_username):
    eligible_users = ["eligible_user", "test_candidate"]  # Hardcoded eligible users
    
    # Check if either username is in the eligible users list
    if github_username in eligible_users or stackoverflow_username in eligible_users:
        return True, "You are eligible! Proceed to the coding challenge."
    
    return False, "Sorry, you are not eligible based on the provided information."

    