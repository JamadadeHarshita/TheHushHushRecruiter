from flask import render_template, redirect, url_for, request  

from app.forms import UsernameForm

def register_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    @app.route('/index', methods=['GET', 'POST'])
    def index():
        form = UsernameForm()
        if form.validate_on_submit():
            github_username = form.github_username.data
            stackoverflow_username = form.stackoverflow_username.data

            eligible, message = check_eligibility(github_username, stackoverflow_username)

            if eligible:
                return redirect(url_for('test_link'))  # Corrected from 'main.test_link' to 'test_link'
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
            print("Code received:", code)
            
            if not code:
                print("No code received, rendering the coding challenge page again.")
                return render_template('coding_challenge.html', error="No code submitted. Please enter your code.")
            
            print("Code submission successful, redirecting to evaluation.")
            return redirect(url_for('evaluation'))
        except Exception as e:
            print("An error occurred:", e)
            return render_template('coding_challenge.html', error="An internal error occurred. Please try again.")

    @app.route('/evaluation')
    def evaluation():
        # Placeholder for the manager's evaluation page
        # Here you'd list all submissions and allow the manager to review them
        return render_template('evaluation.html', submissions=["Sample code 1", "Sample code 2"])


    def check_eligibility(github_username, stackoverflow_username):
        # Mock eligibility check
        eligible_users = ["eligible_user", "test_candidate"]
        
        if github_username in eligible_users or stackoverflow_username in eligible_users:
            return True, "You are eligible! Proceed to the coding challenge."
        return False, "Sorry, you are not eligible based on the provided information."
