from flask import Blueprint, render_template,request,url_for,redirect,flash
from models.user import User
from werkzeug.security import generate_password_hash,check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_login import UserMixin,LoginManager,login_required,logout_user,login_user,current_user

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates/users')


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('new.html')

@users_blueprint.route('/', methods=['POST'])
def create():
    user_password = request.form['password']
    user = User(username=request.form['username'],email=request.form['email'].lower(),password=user_password)
    if user.save():
        login_user(user)
        flash("Successfully signed up and logged in.")
        return redirect(url_for('index'))
    else:
        return render_template('new.html',username=request.form['username'], errors=user.errors)

@users_blueprint.route('/<username>', methods=["GET"])
def show(username):
    user = User.get(User.username == username)
    return render_template('show.html',user=user)
    
@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"


@users_blueprint.route('/<int:id>/edit', methods=['GET'])
def edit(id):
    try:
        if current_user.id==id or current_user.role =='admin':
            user= User.get_by_id(id)
            return render_template('edit.html',user=user)
        return render_template('401.html'), 401    
    except:
        return render_template('401.html'), 401    

@users_blueprint.route('/<int:id>', methods=['POST'])
def update(id):
    if current_user.id==id or current_user.role =='admin':
        user_password = request.form['password']
        user = User.get(User.id == id)
        user.username = request.form['username']
        user.email=request.form['email']
        user.password=user_password
        if user.save():
            flash("Successfully saved.")
            return redirect(url_for('users.edit',id=id))
        return render_template('edit.html',errors=user.errors)
    return render_template('401.html'), 401 