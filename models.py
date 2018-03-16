from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
#from flask.ext.bcrypt import Bcrypt


db = SQLAlchemy()

# bcrypt = Bcrypt()

class User(db.Model):

    __tablename__ = 'users'
    uid = db.Column('username_id', db.Integer, primary_key=True)
    first_name = db.Column('first_name', db.String(100))
    last_name = db.Column('last_name', db.String(100))
    email = db.Column('email', db.String(120), unique=True)
    password_hash = db.Column('password', db.String(50))
    account_verified = db.Column(
        'account_verified', db.Boolean, nullable=False, default=False)
    email_verify_code = db.Column('email_verify_code', db.String(36))
    is_admin = db.Column(
        'is_admin', db.Boolean, nullable=False, default=False)

    def __init__(self, first_name, last_name, email, password, account_verified, email_verify_code, is_admin):
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.email = email.lower()
        self.set_password(password)
        self.account_verified = account_verified
        self.email_verify_code = email_verify_code
        self.is_admin = is_admin

    def set_password(self,password):
        self.password_hash  = generate_password_hash(password)
        #self.password_hash = bcrypt.generate_password_hash(password,10)
        # bycrpt.checkpw(password.encode(), hashed)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)
        #return bcrypt.check_password_hash(self.pwhash, password)
        #if bcrypt.checkpw(password.encode(), hashed):
        #    return True
        #else:
        #    return False

    def check_verified(self):
      if self.account_verified:
          return True
      else:
          return False
