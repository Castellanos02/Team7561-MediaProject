"""
Course: CST205-01_SP23
Title: Team7561 Final Media Project
Abstract: This application allows the user to view a list of foods based on the food ccategory they pick. Once the user selects a specific food. The recpie infromation will be displayed based on the food the user selects. 
Authors: Axel Castellanos, Fabian Santano, Cristobal Elizarraraz, Saul Machuca
Date: 05/17/2023
Github Link: https://github.com/Cast02/Team7561-MediaProject
Citations:
https://www.w3schools.com/css/css3_gradients.asp
https://www.themealdb.com/api.php
https://www.geeksforgeeks.org/login-and-registration-project-using-flask-and-mysql/amp/

"""

from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import MySQLdb.cursors
import mysql.connector
import re
import os
import requests, json

app = Flask(__name__)


app.secret_key = 'your secret key'

search_endpoint = 'https://www.themealdb.com/api/json/v1/1/categories.php'
random_endpoint = "https://www.themealdb.com/api/json/v1/1/random.php"
searchBar_link=f'https://www.themealdb.com/api/json/v1/1/filter.php?i='
payload = {
    'api_key': 1
}


# Set the MySQL connection parameters using environment variables
app.config['MYSQL_HOST'] = 'x71wqc4m22j8e3ql.cbetxkdyhwsb.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'u8e89rp1uw4nc5kn'
#Make sure to change back password
app.config['MYSQL_PASSWORD'] = 'jdgri1ekfyi5afb3'
app.config['MYSQL_DB'] = 'fnfuowcdv3411fa1'


mysql = MySQL(app)
bootstrap = Bootstrap5(app)

#(Cristobal E.)This code creates a flask form for the user to input in asking for the user to input an ingriedient
class SearchBar(FlaskForm):
    user_input=StringField(
        'Search By Ingriedient:',
        validators=[DataRequired()]
    )
data_search=None

def home():
    return render_template('index.html')

@app.route('/new_User')
def newPage():
    return render_template('introPage.html')

#Fabian
#This is the loggin page , used flask-forms , flask mysql and flask sessions to verify username is
# unique and not already in the database if successful you will be rendered into home page
@app.route('/', methods=['GET', 'POST'])
def returing():
    msg = ''
    form=SearchBar()
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


            try:
                r = requests.get(random_endpoint, params=payload)
                data_random = r.json()
            except:
                print("please try again")
            
            return render_template('homePage.html', msg=msg, data=data_random ,form = form)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)

#Fabian
#Sign up Page Uses same features as loggin but this time we check and make sure the passowrd and username match anything in our dataBase 
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
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s)', (username, password,))
            mysql.connection.commit()
            cursor.execute('INSERT INTO accountrecipes VALUES (%s, %s, %s,%s,%s,%s,%s)', (username, "0","0","0",0,0,0))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('newPage'))
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('createAccount.html', msg=msg)

#Fabian Simple Logout button
@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('returing'))



@app.route('/home_Page', methods=['GET', 'POST'])
def homePage():
    form=SearchBar()
    global data_search
    if form.validate_on_submit():#(Cristobal E.)This code validates the form that takes in the users input for the search bar
        lower_case=  form.user_input.data.lower()#(Cristobal E.)This code forces all input to be lower case letters
        presearch=lower_case.replace(" ", "_" )#(Cristobal E.)This code replaces any spaces inputed to become _ symbols so it works with the API link
        searchbar(presearch)
        print(data_search)
        return redirect('/results')
    else:
        print("form not valid")

    random_endpoint = "https://www.themealdb.com/api/json/v1/1/random.php"
    try:
        r = requests.get(random_endpoint, params=payload)
        data_random = r.json()
    except:
        print("please try again")
    return render_template('homePage.html', data=data_random, form=form)

@app.route('/results', methods=['GET','POST'])
def results():
    global data_search
    if data_search==None:#(Cristobal E.)This if statement checks if the users input is empty and if so just redirects the back to the home page
        return redirect('/home_Page')
    else:#(Cristobal E.)This code will render the results page for the search bar
        return render_template('searchByIngriedient.html', data=data_search)
#(Cristobal E.)This function performs a search using a search bar input and stores the results in the 'data_search' variable, handling exceptions.
def searchbar(user_input):
    global data_search
    try:
        search_endpoint=searchBar_link+user_input
        s = requests.get(search_endpoint, params=payload)
        data_search = s.json()
        # return data_search
    except:
        print('Please try again')

# Axel Castellanos-Morales
@app.route('/search_Item')
def search():
    try:
        # this request grabs all the food categories the API has to offer
        s = requests.get(search_endpoint, params=payload)
        data_search = s.json()
    except:
        print('Please try again')
    return render_template('searchByCategory.html', data=data_search)

# Axel Castellanos-Morales
@app.route('/list_category/<category>')
def listCategory(category):
    # used an f string to update the endpoint with the category the user selected
    list_endpoint = f'https://www.themealdb.com/api/json/v1/1/filter.php?c={category}'
    print(list_endpoint)
    try:
        # this request gets all the food that is under the specified food category
        l = requests.get(list_endpoint, params=payload)
        data_category = l.json()
    except:
        print('Please Try Again')
    return render_template('categoryList.html', data=data_category, category=category)

@app.route('/list_ingredient/<ingredient>')
def listIngredient(ingredient):
    list_endpoint = f'https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}'
    print(list_endpoint)
    try:
        i = requests.get(list_endpoint, params=payload)
        data_ingredient = i.json()
    except:
        print('Please Try Again')
    return render_template('ingredientList.html', data=data_ingredient, ingredient=ingredient)

@app.route('/food_Information/<id>/<category>')
def foodInfo(id, category):
    # used another f string to update the endpoint witht the id of the specfifc food the user chose
    # also have category as a pramater so that when the user goes back to the route '/list_category/<category>' the category paramater will have the same 
    food_endpoint = f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}'
    try:
        # this request gets recipe information about the specific food
        f = requests.get(food_endpoint, params=payload)
        data_food = f.json()
    except:
        print("Please Try Again")
    return render_template('specificFood.html', category=category, data=data_food)

#Fabian , loops though all saved recipes in the users database to match the delted mealID 
# then we set the ifIdIsEmpty to 0 indicatating we can overwrite this. 
@app.route('/delete-id', methods=['POST'])
def deleteIdToDatabase():
    form=SearchBar()
    global isEmpty1
    global isEmpty2 
    global isEmpty3
    msg = ''
    username = session.get('username')
    emptyMealID = 0
    meal_id = request.form.get('meal_id')
    recipeSQL = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    recipeSQL.execute(
            'SELECT * FROM accountrecipes WHERE username = % s', (username, ))
    account = recipeSQL.fetchone()

    if account['mealID1'] == meal_id:
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE accountrecipes SET id1IsEmpty = %s WHERE username = %s', (0, username))
        mysql.connection.commit()
        msg = 'You have deleted successfully!'
        random_endpoint = "https://www.themealdb.com/api/json/v1/1/random.php"
        isEmpty1 = 0
        try:
            r = requests.get(random_endpoint, params=payload)
            data_random = r.json()
        except:
            print("please try again")
        return render_template('homePage.html', data=data_random , form = form )

    if account['mealID2'] == meal_id:
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE accountrecipes SET id2IsEmpty = %s WHERE username = %s', (0, username))
        mysql.connection.commit()
        msg = 'You have deleted successfully!'
        random_endpoint = "https://www.themealdb.com/api/json/v1/1/random.php"
        isEmpty2 = 0
        try:
            r = requests.get(random_endpoint, params=payload)
            data_random = r.json()
        except:
            print("please try again")
        return render_template('homePage.html', data=data_random , form = form )

    if account['mealID3'] == meal_id:
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE accountrecipes SET id3IsEmpty = %s WHERE username = %s', (0, username))
        mysql.connection.commit()
        msg = 'You have deleted successfully!'
        random_endpoint = "https://www.themealdb.com/api/json/v1/1/random.php"
        try:
            r = requests.get(random_endpoint, params=payload)
            data_random = r.json()
        except:
            print("please try again")
        return render_template('homePage.html', data=data_random , form = form )
        

#Fabian Uses a form and button to add the mealId to the users database so they can later view the recipe
#Updates an empty mealid to the form meal id and then updates theIsEmpty to 1 indicating its full and in use.
@app.route('/add-id', methods=['POST'])
def addIdToDatabase():
    form=SearchBar()
    msg = ''
    emptyMealID = 0
    username = session.get('username')
    meal_id = request.form.get('meal_id')




    recipeSQL = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    recipeSQL.execute(
            'SELECT * FROM accountrecipes WHERE username = % s', (username, ))
    account = recipeSQL.fetchone()
    if account["id1IsEmpty"]== 0:
        emptyMealID=1
    elif account["id2IsEmpty"]== 0:
        emptyMealID=2
    elif account["id3IsEmpty"]== 0:
        emptyMealID=3
    
    if emptyMealID == 0:
        return render_template('homePage.html', data=data_random)

    else:
        recipeSQLUpdate = mysql.connection.cursor()
        query = "UPDATE accountrecipes SET mealID{} = %s WHERE username = %s".format(emptyMealID)
        values = (meal_id, username)
        recipeSQLUpdate.execute(query, values)
        mysql.connection.commit()
        recipeSQLUpdate = mysql.connection.cursor()
        query = "UPDATE accountrecipes SET id{}IsEmpty = %s WHERE username = %s".format(emptyMealID)
        values = (1, username)
        recipeSQLUpdate.execute(query, values)
        mysql.connection.commit()
        msg = 'You have added successfully!'
        random_endpoint = "https://www.themealdb.com/api/json/v1/1/random.php"
        try:
            r = requests.get(random_endpoint, params=payload)
            data_random = r.json()
        except:
            print("please try again")
        return render_template('homePage.html', data=data_random , form = form)

#Fabian Displays all saved recipes from users database
@app.route("/displayInfo")
def display():
    meal_id = request.form.get('meal_id')
    emptyMealID = 0
    global isEmpty1
    global isEmpty2
    global isEmpty3
    
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accountrecipes WHERE username = % s',
                       (session['username'], ))
        account = cursor.fetchone()
        id1 = account['mealID1']
        id2 = account['mealID2']
        id3 = account['mealID3']
        if account['id1IsEmpty'] == 0:
            isEmpty1=1
        if account['id2IsEmpty'] == 0:
            isEmpty2=1
        if account['id3IsEmpty'] == 0:
            isEmpty3=1
            
        food_endpoint1 = f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={id1}'
        food_endpoint2 = f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={id2}'
        food_endpoint3 = f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={id3}'

        
        f1 = requests.get(food_endpoint1, params=payload)
        f2 = requests.get(food_endpoint2, params=payload)
        f3 = requests.get(food_endpoint3, params=payload)
        data_food1 = f1.json()
        data_food2 = f2.json()
        data_food3 = f3.json()
        if account['mealID1'] != "" or account['mealID2'] != "" or account['mealID3'] != "":
            return render_template("display.html", account=account,data1=data_food1,data2=data_food2,data3=data_food3 )
    return redirect(url_for('returing'))

    if __name__ == "__main__":
	    app.run(host="localhost", port=int("5000"))