# print("Hello")

from flask import Flask, render_template
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
bootstrap = Bootstrap5(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/new_User')
def newPage():
    return render_template('introPage.html')

@app.route('/returing_User')
def returing():
    return render_template('homePage.html')

@app.route('/create_User')
def newUser():
    return render_template('createAccount.html')
# This is just a test to see if my commit is working