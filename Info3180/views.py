"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from Info3180 import app
from flask import Flask, render_template, request, redirect, url_for, jsonify, g, flash, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from bs4 import BeautifulSoup
import os
import requests

app.config['SECRET_KEY'] = 'Info3180'
if os.environ.get('INFO3180_URL') is None:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:3180@localhost/info3180'
else: 
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['INFO3180_URL']

db = SQLAlchemy(app)
import Info3180.models
auth = HTTPBasicAuth()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return Info3180.models.User.query.get(int(id))

@app.route('/login')
def loginform():
    return render_template('login.html')

@app.route('/register')
def registerform():
    return render_template('register.html')

@app.route('/api/user/login', methods=['POST'])
def login():
    if request.headers.get('Content-Type') == 'application/json':
        email = request.json.get('email')
        password = request.json.get('password')
        
        user = Info3180.models.User.query.filter_by(email = email).first()
        if user and user.verify_password(password):
            login_user(user)
            data = { 'error' : None,'data':  {'token' : get_auth_token(), 'user': {'_id' : user.id, 'email' : user.email, 'name': user.username}, 'message' : 'Success'}}
            return jsonify(response=data)
    else:
        email = request.form['email']
        password = request.form['password']
        user = Info3180.models.User.query.filter_by(email = email).first()
        if user and user.verify_password(password):
            login_user(user)
            data = { 'error' : None, 'data':  {'token' : get_auth_token(), 'user': {'_id' : user.id, 'email' : user.email, 'name': user.username}, 'message' : 'Success'}}
            return redirect('/add_item/' + str(user.id), 302)
            
    flash('Incorrect Credentials Entered')
    data = {'error' : '1', 'data': {}, 'message': 'Incorrect credentials entered'}
    return jsonify(response=data)

@app.route('/add_item/<id>', methods=['GET'])
@login_required
def add_item_view(id):
    action = '/api/user/' + str(id) + '/wishlist'
    return render_template('add_item.html', id=id, action=action)

@app.route('/api/user/register', methods=['POST'])
def register_user():
    if request.headers.get('Content-Type') == 'application/json':
        email = request.json.get('email')
        name = request.json.get('name')
        password = request.json.get('password')
        if email is None or password is None or name is None:
            abort(400)
        if Info3180.models.User.query.filter_by(email = email).first() is not None:
            return 'User already exists. Try logging in'
        user = Info3180.models.User(username = name, email = email)
        user.hash_password(password)
        user.email = email
        db.session.add(user)
        db.session.commit()
        data = { 'error' : None, 'data':  {'token' : get_auth_token(), 'user': {'_id' : user.id, 'email' : user.email, 'name': user.username}, 'message' : 'Success'}}
        return jsonify(response=data)
    else:
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']

        if email is None or password is None or name is None:
            abort(400)
        if Info3180.models.User.query.filter_by(email = email).first() is not None:
            return 'User already exists. Try logging in'
        user = Info3180.models.User(username = name, email = email)
        user.hash_password(password)
        user.email = email
        db.session.add(user)
        db.session.commit()
        data = { 'error' : None, 'data':  {'token' : get_auth_token(), 'user': {'_id' : user.id, 'email' : user.email, 'name': user.username}, 'message' : 'Success'}}
        return jsonify(response=data)
    return 'Error'


@login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return token.decode('ascii')
    
@login_required
@app.route('/api/thumbnail/process', methods=['GET'])
def crawl():
        try:
            url = request.args['url']
            page = requests.get(url)
            parsed_page = BeautifulSoup(page.text, 'html.parser')
            imgs = [img.get('src') for img in parsed_page.find_all('img')]
            imgs = [img for img in imgs if img.startswith('http')]
            if len(imgs) > 0:
                data = {'error':None, 'data': { 'thumbnails': imgs }, 'message':'Success'}
                return jsonify(response=data)
        except Exception as x:
            return str(x) 
        data = {'error':'1', 'data': {}, 'message':'Unable to extract thumbnails from given url'}
        return jsonify(respone=data)
            
@login_required
@app.route('/api/user/<id>/wishlist', methods=['POST', 'GET'])
def add_item(id):
    if request.method == 'POST':
        if request.headers.get('Content-Type') == 'application/json':
            userid = id
            title = reequest.json.get('title')
            desc = request.json.get('description')
            image_url = request.json.get('thumbnail')
            item_url = request.json.get('url')
            
            if image_url is None:
                image_url = '../static/images/Wishlist.jpg'
            if Info3180.models.Wishlist.query.filter_by(item_url = item_url).first() is not None:
               data = {'error':'1', 'data': {}, 'message': 'Wishlist item already exists'} 
               return jsonify(response=data) 
            item = Info3180.models.Wishlist(title, desc, item_url, image_url, userid)
            db.session.add(item)
            db.session.commit()
            data = {'error': None, 'data': {'title': title, 'description' : desc}, 'message': 'Success'}
            return jsonify(response=data)             
        else: 
            userid = id
            title = request.form['title']
            desc = request.form['description']
            image_url = request.form['thumbnail']
            item_url = request.form['url']
            
            if image_url is None:
                image_url = '../static/images/Wishlist.jpg'
            if Info3180.models.Wishlist.query.filter_by(item_url = item_url).first() is not None:
               data = {'error':'1', 'data': {}, 'message': 'Wishlist item already exists'} 
               return jsonify(response=data) 
            item = Info3180.models.Wishlist(title, desc, item_url, image_url, userid)
            db.session.add(item)
            db.session.commit()
            data = {'error': None, 'data': {'title': title, 'description' : desc}} 
            return jsonify(response=data) 
        return 'Success i guess' 
    else:
        wishlist_items = Info3180.models.Wishlist.query.filter_by(userid=id).all()
        if wishlist_items != []:
            data = {'error': None, 'data': {'wishes': [{'title':item.title, 'description':item.description, 'url':item.item_url, 'thumbnail':item.image_url} for item in wishlist_items]}, 'message': 'Success'}
            return jsonify(response=data, test=str(wishlist_items))
        else:
            data = {'error': '1', 'data' : {}, 'message':'No such wishlist exists'}
            return jsonify(response=data)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login', 302)



































@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.before_request
def before_request():
    g.user = current_user
@auth.verify_password
def verify_password(username_or_token, password):
    #Authenticate by token
    user = Info3180.models.User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = Info3180.models.User.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

    