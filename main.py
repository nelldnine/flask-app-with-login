import hashlib
from flask import Flask, render_template, request, url_for, redirect, session
from settings import SECRET, SALT
from models.user import User

app = Flask(__name__)
app.secret_key = SECRET

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = hashlib.md5(SALT + request.form.get('password')).hexdigest()
        user = User.query(User.email == request.form.get('email')).get()
        if user and user.password == password:
            session['user'] = user.name
            return redirect(url_for('dashboard'))
        return redirect(url_for('login', error='Invalid email and/or password'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            email=request.form.get('email'),
            password=hashlib.md5(SALT + request.form.get('password')).hexdigest(),
            name=request.form.get('name')
        )
        user.put()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    del session['user']
    return redirect(url_for('index'))
