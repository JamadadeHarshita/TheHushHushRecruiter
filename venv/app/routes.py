from flask import render_template, redirect, url_for, request
from app.models import Submission, Feedback, db  # Assuming you have these models
from app.forms import UsernameForm

def register_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def index():
        form = UsernameForm()
        if form.validate_on_submit():
            github_username = form.github_username.data
            stackoverflow_username = form.github_username.data

            eligible, message = check_eligibility(github_username, stackoverflow_username)

            if eligible:
                return redirect(url_for('test_link'))
            else:
                return render_template('eligibility_result.html', message=message)
        
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

            print(f"Feedback submitted for submission {submission_id}: {feedback_text} with score {score}")

            return redirect(url_for('evaluation'))

        return render_template('feedback.html', submission=submission)


def check_eligibility(github_username, stackoverflow_username):
    eligible_users = ["eligible_user", "test_candidate"]
    
    if github_username in eligible_users or stackoverflow_username in eligible_users:
        return True, "You are eligible! Proceed to the coding challenge."
    return False, "Sorry, you are not eligible based on the provided information."
