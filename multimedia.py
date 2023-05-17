# print("Hello")

from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import mysql.connector
import re
import os
import requests, json

app = Flask(__name__)


app.secret_key = 'your secret key'

# search_endpoint = 'https://www.themealdb.com/api/json/v1/1/list.php?c=list'
search_endpoint = 'https://www.themealdb.com/api/json/v1/1/categories.php'
payload = {
    'api_key': 1
}


# Set the MySQL connection parameters using environment variables
app.config['MYSQL_HOST'] = 'x71wqc4m22j8e3ql.cbetxkdyhwsb.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'u8e89rp1uw4nc5kn'
#Make sure to change back password
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

@app.route('/home_Page')
def homePage():
    return render_template('homePage.html')

@app.route('/search_Item')
def search():
    try:
        s = requests.get(search_endpoint, params=payload)
        data_search = s.json()
    except:
        print('Please try again')
    return render_template('searchByCategory.html', data = data_search)

@app.route('/list_category/<category>')
def listCategory(category):
    list_endpoint = f'https://www.themealdb.com/api/json/v1/1/filter.php?c={category}'
    print(list_endpoint)
    try:
        l = requests.get(list_endpoint, params=payload)
        data_category = l.json()
    except:
        print('Please Try Again')
    return render_template('categoryList.html', data=data_category, category=category)

@app.route('/food_Information/<id>/<category>')
def foodInfo(id, category):
    food_endpoint = f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}'
    try:
        f = requests.get(food_endpoint, params=payload)
        data_food = f.json()
    except:
        print("Please Try Again")
    return render_template('specificFood.html', category=category, data=data_food)