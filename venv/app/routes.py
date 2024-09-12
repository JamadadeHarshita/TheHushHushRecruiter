from flask import render_template, redirect, url_for, request
from app.models import Submission, Feedback, db  # Assuming you have these models
from app.forms import UsernameForm
from flask_mail import Message
from app import mail


# Send the test link to eligible users via email
def send_test_link_email(username):
    recipient_email = "jamadadeharshita@gmail.com"  # Send to this email for testing
    msg = Message("Coding Challenge Invitation",
                  recipients=[recipient_email])
    
    msg.body = f"""
    Hi {username},

    Congratulations! Based on your profile, you're invited to participate in a coding test.

    Please use this link to take the test: http://127.0.0.1:5000/test_link

    Best regards,
    Doodle Recruitment Team
    """
    
    # Send the email using Flask-Mail
    mail.send(msg)


# Send feedback emails to candidates
def send_feedback_email(username, feedback_text=None, score=None):
    recipient_email = "engineerdata061@gmail.com"  # Use your email for testing
    
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

        if request.method == 'POST':
            # Check if form is submitted
            print("Form submitted")

            # Check if the form validates
            if form.validate_on_submit():
                print("Form validated successfully")
                github_username = form.github_username.data
                stackoverflow_username = form.stackoverflow_username.data

                # Debugging
                print(f"GitHub Username: {github_username}, Stack Overflow Username: {stackoverflow_username}")

                # Check eligibility
                eligible, message = check_eligibility(github_username, stackoverflow_username)

                # Debugging the result
                print(f"Eligibility: {eligible}, Message: {message}")

                if eligible:
                    send_test_link_email(github_username or stackoverflow_username)
                    return redirect(url_for('submission_confirmation'))
                else:
                    return render_template('eligibility_result.html', message=message)
            else:
                print("Form validation failed")
        
        # If it's a GET request or the form is invalid, render the index page
        return render_template('index.html', form=form)

    @app.route('/test_link')
    def test_link():
        return render_template('coding_challenge.html')

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

    