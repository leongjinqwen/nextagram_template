import os
import config
from flask import Flask,render_template,request,url_for,redirect,flash,escape
from models.base_model import db
from models.user import User
from werkzeug.security import generate_password_hash,check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_login import UserMixin,LoginManager,login_required,logout_user,login_user,current_user
from helpers import *
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

web_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'instagram_web')

app = Flask('NEXTAGRAM', root_path=web_dir)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = "user"

if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

@app.before_request
def before_request():
    db.connect()

@app.after_request
def after_request(response):
    db.close()
    return response

@app.route('/')
def index():
    return render_template('home.html')

@app.route("/new_user")
def new_user():
    return render_template('signup.html')

@app.route("/sign_up",methods=["POST"])
def sign_up():
    user_password = request.form['password']
    user = User(username=request.form['username'],email=request.form['email'].lower(),password=user_password)
    if user.save():
        login_user(user)
        flash("Successfully signed up and logged in.")
        return redirect(url_for('index'))
    else:
        return render_template('signup.html',username=request.form['username'], errors=user.errors)

@app.route("/users")
def user():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        return render_template('login.html')

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

@app.route("/login",methods=["GET","POST"])
def login():
    user = User.get_or_none(User.username == request.form['username'])
    if user :
        password_to_check = request.form['password']
        hashed_password = user.password
        result = check_password_hash(hashed_password, password_to_check)
        if result :
            login_user(user)
            flash("Successfully logged in.")
            return redirect(url_for('index'))
        else:
            error = "Please fill in valid username and password."
            return render_template('login.html',error=error)
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Successfully logged out.")
    return redirect(url_for('index'))

@app.route('/users/<username>')
def show_profile(username):
    user = User.get(User.username == username)
    return render_template('profile.html',user=user)
    
@app.route('/users/<int:id>/edit')
def edit_page(id):
    try:
        if current_user.id==id or current_user.role =='admin':
            user= User.get_by_id(id)
            return render_template('edit_info.html',user=user)
        return render_template('401.html'), 401    
    except:
        return render_template('401.html'), 401    

@app.route('/users/<int:id>/editing',methods=["POST"])
def edit_info(id):
    if current_user.id==id or current_user.role =='admin':
        user_password = request.form['password']
        user = User.get(User.id == id)
        user.username = request.form['username']
        user.email=request.form['email']
        user.password=user_password
        if user.save():
            flash("Successfully saved.")
            return redirect(url_for('edit_page',id=id))
        return render_template('edit_info.html',errors=user.errors)
    return render_template('401.html'), 401 

def upload_file_to_s3(file, bucket_name, acl="public-read"):
    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        flash("Something Happened: ", e)
        return e
    return "{}{}".format(app.config["S3_LOCATION"], file.filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/users/upload',methods=["POST"])
def profile_photo():
    if "user_file" not in request.files:
        return "No user_file key in request.files"
    file = request.files["user_file"]
    if file.filename == "":
        return "Please select a file"
    if file and allowed_file(file.filename):
        file.filename = secure_filename(file.filename)
        output = upload_file_to_s3(file, app.config["S3_BUCKET"])
        return str(output)
    else:
        return render_template('edit_info.html')



@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

