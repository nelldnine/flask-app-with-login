import hashlib
import cloudstorage as gcs
from flask import Flask, render_template, request, url_for, redirect, session, jsonify
from settings import SECRET, SALT, BUCKET_NAME
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
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query(User.email == email).get()
        if not user:
            user = User(
                email=email,
                password=hashlib.md5(SALT + password).hexdigest(),
                name=request.form.get('name')
            )
            user.put()
        else:
            return redirect(url_for('register', error='Email is already taken'))
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        response = {}
        f = request.files['file']
        filename = '{}/{}'.format(BUCKET_NAME, f.filename)
        gcs_options = {'x-goog-acl': 'public-read'}
        gcs_file = gcs.open(filename, 'w', options=gcs_options)
        gcs_file.write(f.read())
        gcs_file.close()
        response['file_url'] = 'https://storage.googleapis.com' + filename
        return redirect(url_for('upload'))
    return render_template('upload.html')

@app.route('/logout')
def logout():
    del session['user']
    return redirect(url_for('index'))
