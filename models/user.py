from models.base_model import BaseModel
import peewee as pw
from werkzeug.security import generate_password_hash
from flask_login import UserMixin

class User(UserMixin,BaseModel):
    username = pw.CharField(unique=True,null=False)
    email = pw.CharField(unique=True,null=False)
    password = pw.CharField(null=False)

    def validate(self):
        duplicate_username = User.get_or_none(User.username == self.username)
        duplicate_email = User.get_or_none(User.email == self.email)
        if duplicate_username:
            self.errors.append('Username not unique')
        if duplicate_email:
            self.errors.append('Email not unique')
        if len(self.password) < 8 or len(self.password) > 25:
            self.errors.append('Password must between 8-25 characters.')
        else:
            self.password=generate_password_hash(self.password)