from flask import Flask, render_template, redirect, session, request, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
app = Flask(__name__)
app.secret_key = 'SHHHH'
bcrypt = Bcrypt(app)
import re 
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

mysql = connectToMySQL('login_registrationdb')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_user():
    session['first_name'] = request.form['first_name']
    session['last_name'] = request.form['last_name']
    session['email'] = request.form['email']
    session['password'] = request.form['password']
    session['confirm'] = request.form['confirm']
    query = 'SELECT * FROM users WHERE users.email = %(email)s;'
    data = {'email': request.form['email']}
    result = mysql.query_db(query,data)
    if len(session['first_name']) < 3 or len(session['first_name']) < 1:
        flash('First name must contain at least 2 characters')
        return redirect('/')
    elif re.search('[0-9]',session['first_name']) is not None:
        flash('Name can only contain letters')
        return redirect('/')
    if len(session['last_name']) < 3 or len(session['last_name']) < 1:
        flash('Last name must contain at least 2 characters')
        return redirect('/')
    elif re.search('[0-9]', session['last_name']) is not None:
        flash('Name can only contain letters')
        return redirect('/')
    if not EMAIL_REGEX.match(session['email']):
        flash('Invalid Email')
        return redirect('/')
    elif len(result) > 0:
        flash('Email already taken')
        return redirect('/')
    if len(session['password']) < 8 or len(session['password']) < 1:
        flash('Password must be at least 8 characters long')
        return redirect('/')
    elif session['password'] != session['confirm']:
        flash('Passwords must match')
        return redirect('/')
    elif re.search('[A-Z]', session['password']) is None:
        flash('Password must contain at least one capital letter')
        return redirect('/')
    elif re.search('[0-9]', session['password']) is None:
        flash('Password must contain at least one number')
        return redirect('/')
    if int(request.form['birthday'][:4]) > 2010:
        flash('You must be at least 10 years old to register')
        return redirect('/')
    else:
        query = 'INSERT INTO users(first_name, last_name, email, created_at, updated_at, password, birthday, fav_color) VALUES (%(first_name)s, %(last_name)s, %(email)s, NOW(), NOW(), %(password)s, %(birthday)s, %(fav_color)s);'
        data = {
                'first_name' : request.form['first_name'],
                'last_name' : request.form['last_name'],
                'email' : request.form['email'],
                'password': request.form['password'], 
                'birthday': request.form['birthday'],
                'fav_color': request.form['fav_color']
                }
        mysql.query_db(query,data)
        flash('Thanks for submitting!')
        return redirect('/')

@app.route('/login', methods=['POST'])
def login_user():
    query = 'SELECT * FROM users WHERE users.email = %(email)s AND users.password = %(password)s;'
    data ={ 'email' : request.form['email'], 'password' :request.form['pw']  }
    result = mysql.query_db(query, data)
    if 'id' in session:
        if session['id'] == result[0]['id']:
            flash('You are already logged in')
            return redirect('/')
    if len(result) == 1:
        session['id'] = result[0]['id']
        flash('You have logged in')
        return redirect('/')
    else:
        flash('Invalid Login Info')
        return redirect('/')



    

    

app.run(debug=True)