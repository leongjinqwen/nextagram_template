from models.base_model import BaseModel
import peewee as pw
from werkzeug.security import generate_password_hash
from flask_login import UserMixin
from playhouse.hybrid import hybrid_property
from app import app
import datetime
import jwt

class User(UserMixin,BaseModel):
    username = pw.CharField(unique=True,null=False)
    email = pw.CharField(unique=True,null=False)
    password = pw.CharField(null=False)
    role = pw.CharField(null=False,default='user')
    profile_pic = pw.TextField(default="13defaultpic.png2019-02-22_115512.565685")
    private = pw.BooleanField(default=False)
    bio = pw.TextField(default='The NEXT star!')
    
    def validate(self):
        duplicate_username = User.get_or_none(User.username == self.username)
        duplicate_email = User.get_or_none(User.email == self.email)
        if duplicate_username and duplicate_username.id != self.id:
            self.errors.append('Username not unique')
        if duplicate_email and duplicate_email.id != self.id :
            self.errors.append('Email not unique')
        if len(self.password) < 8 or len(self.password) > 25:
            self.errors.append('Password must between 8-25 characters.')
        else:
            self.password=generate_password_hash(self.password)

    @hybrid_property
    def profile_image_url(self):
        if self.profile_pic:
            return app.config['AWS_S3_DOMAIN'] + self.profile_pic
        else:
            return app.config['AWS_S3_DOMAIN'] + "13defaultpic.png2019-02-22_115512.565685"

    
    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 0
        except jwt.InvalidTokenError:
            return 0