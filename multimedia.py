# print("Hello")

from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import mysql.connector
import re
import os
app = Flask(__name__)


app.secret_key = 'your secret key'




# Set the MySQL connection parameters using environment variables
app.config['MYSQL_HOST'] = 'x71wqc4m22j8e3ql.cbetxkdyhwsb.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'u8e89rp1uw4nc5kn'
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = 'fnfuowcdv3411fa1'


mysql = MySQL(app)
bootstrap = Bootstrap5(app)



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/new_User')
def newPage():
    return render_template('introPage.html')

@app.route('/returing_User', methods=['GET', 'POST'])
def returing():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password'] 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE username = % s \
            AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['password'] = account['password']
            msg = 'Logged in successfully !'
            return render_template('homePage.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)


#Sign up Page
@app.route('/create_User', methods=['GET', 'POST'])
def newUser():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        # elif not re.match(r'[A-Za-z0-9]+', username):
        #     msg = 'Name must contain only characters and numbers!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s)', (username, password,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('newPage'))
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('createAccount.html', msg=msg)


@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('returing'))


if __name__ == "__main__":
	app.run(host="localhost", port=int("5000"))
