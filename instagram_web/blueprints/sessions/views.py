from flask import Blueprint, render_template,request,url_for,redirect,flash
from models.user import User
from werkzeug.security import generate_password_hash,check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_login import UserMixin,LoginManager,login_required,logout_user,login_user,current_user
from app import app
from instagram_web.util.google_oauth import oauth
import os

sessions_blueprint = Blueprint('sessions',
                            __name__,
                            template_folder='templates')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "sessions.new"

@sessions_blueprint.route("/new", methods=['GET'])
def new():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        return render_template('sessions/new.html')

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

@sessions_blueprint.route("/login", methods=["GET","POST"])
def login():
    user = User.get_or_none(User.username == request.form['username'])
    if user :
        password_to_check = request.form['password']
        hashed_password = user.password
        result = check_password_hash(hashed_password, password_to_check)
        if result :
            login_user(user)
            flash("Successfully logged in.",'primary')
            return redirect(url_for('index'))
        else:
            flash("Please fill in valid username and password.",'danger')
            return render_template('sessions/new.html')
    
@sessions_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Successfully logged out.",'primary')
    return redirect(url_for('sessions.new'))

@sessions_blueprint.route("/google",methods=["GET"])
def google():
    redirect_uri = url_for('sessions.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)
    
@sessions_blueprint.route('/authorize/google')
def authorize():
    token = oauth.google.authorize_access_token()
    email = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()['email']
    user = User.get_or_none(User.email == email)
    if user :
        login_user(user)
        flash("Successfully logged in.",'primary')
        return redirect(url_for('index'))
    else:
        name = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()['name']
        user_password = os.urandom(8)
        user = User(username=name.lower(),email=email,password=user_password)
        user.save()
        login_user(user)
        flash("Successfully signed up and logged in.","primary")
        return redirect(url_for('index'))