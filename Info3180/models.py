from flask.ext.sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as password_context
from Info3180.views import db
from Info3180.views import app
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(40), unique=True, index=True)
    email = db.Column(db.String(40), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    
    def hash_password(self, password):
        self.password_hash = password_context.encrypt(password)

    def verify_password(self, password):
        return password_context.verify(password, self.password_hash)
        
    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return self.id
        
    def generate_auth_token(self, expiration = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })
        
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user
   
   
class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(2000))
    item_url = db.Column(db.String(255))
    image_url = db.Column(db.String(300))
    userid = db.Column(db.Integer)
    
    def __init__(self, title, desc, item_url, img_url, userid):
        self.title = title 
        self.description = desc 
        self.item_url = item_url
        self.image_url = img_url
        self.userid = userid