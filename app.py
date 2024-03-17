from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import session
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set your own secret key for session management

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define a User model for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone_number = db.Column(db.String(15))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the user exists in the database and the password is correct
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['name'] = user.name
            print("Session name:", session.get("name"))
            flash('Login successful', 'success')
            return redirect(url_for('userhome'))
        else:
            flash('Login failed. Please check your credentials.', 'danger')

    return render_template('login.html')

@app.route('/signup.html', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['number']
        username = request.form['username']
        password = request.form['password']

        # Check if the user already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
        else:
            # Create a new user in the database
            new_user = User(name=name, email=email, phone_number=phone_number, username=username, password=password)
            db.session.add(new_user)
            db.session.commit()

            flash('Signup successful', 'success')
            return redirect(url_for('login'))

        return render_template('signup.html')


@app.route('/userhome', methods=['GET', 'POST'])
def userhome():
    return render_template('userhome.html')

college_data = pd.read_csv('colleges.csv')

# Function to recommend colleges and courses based on marks and courses
def recommend_colleges(marks, courses):
    cleaned_courses = courses.replace(" ", "").strip().lower()  # Remove spaces and normalize input
    recommended_colleges = college_data[
        (college_data['RequiredMarks'] <= marks) &
        (college_data['Courses'].str.replace(" ", "").str.strip().str.lower() == cleaned_courses)
    ]
    return recommended_colleges.to_dict(orient='records')


@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_marks = request.form.get('user_marks', '')
    user_courses = request.form.get('user_courses', '')

    try:
        marks = int(user_marks)
        if marks >= 0:
            recommended_colleges = recommend_colleges(marks, user_courses)
        else:
            recommended_colleges = []
    except ValueError:
        recommended_colleges = []

    return jsonify({'bot_response': recommended_colleges})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create the database and tables
    app.run(debug=True, port=5500)
