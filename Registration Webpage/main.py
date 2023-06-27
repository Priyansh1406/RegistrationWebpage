from flask import Flask,session
from flask import render_template
from flask import request
from flask import flash
from flask import redirect,url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from flask_login import login_required, current_user
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
import yaml
import os



app = Flask(__name__)
app.secret_key = os.urandom(24)

# configure db
db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['SECRET_KEY'] = 'priyanshpandey14'

mysql = MySQL(app)

@app.route('/')
def index():
    return redirect(url_for('signup'))

@app.route('/sign-up')
def signup():
    return render_template("sign-up.html")

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form.get('email')
        password = request.form.get('password')
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email LIKE %s and password LIKE %s" , [email,password])
        account = cursor.fetchall()
        if account:
            flash('Logged in successfully!',category ='success')
            # session['First_Name'] = account[0][0]
            return redirect(url_for('show'))
        else:
            flash('Incorrect Email ID or Password',category='error')
        
    return render_template("login.html")
     

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/login_validation', methods=['POST','GET'])
def login_validation():
    if request.method == 'POST':
        userDetails = request.form
        first_name=userDetails['firstName']
        last_name=userDetails['lastName']
        email=userDetails['email']
        password1=userDetails['password1']
        password2=userDetails['password2']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email LIKE %s" , [email])
        emailExist = cursor.fetchone()
        if emailExist:
            flash('Email already exists', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(last_name) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash("Passwords don't match.", category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            hash = password1 + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password1 = hash.hexdigest()
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users(first_name,last_name,email,password) VALUES(%s,%s,%s,%s)",(first_name,last_name,email,password1))
            mysql.connection.commit()
            cur.close()
            flash('Account Created Successfully!', category='success')
            return redirect(url_for('login'))

    return render_template('sign-up.html')

@app.route('/show')
def show():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT First_Name,Last_Name,email,password FROM users")
    if result>0:
        userDetails = cur.fetchall()
        return render_template('show.html',userDetails=userDetails)
    else:
        flash("No data found!", category="error")

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')

