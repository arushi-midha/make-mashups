from flask import Flask, request, render_template, redirect, url_for
import subprocess
from validate_email_address import validate_email

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-mashup', methods=['POST'])
def create_mashup():
    # Get form data
    singer_name = request.form['singer_name']
    n_videos = request.form['n_videos']
    duration = request.form['duration']
    output_file = request.form['output_file']
    email = request.form['email']

    # Validate inputs
    if not validate_email(email):
        return "Invalid email address.", 400

    # Run the Python script with subprocess
    try:
        result = subprocess.run(['python', 'mashup_script.py', singer_name, n_videos, duration, output_file],
                                capture_output=True, text=True)
        
        # Display the output or any error
        if result.returncode != 0:
            return f"Error occurred: {result.stderr}", 500
        return f"Mashup created and sent to {email}!"
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
