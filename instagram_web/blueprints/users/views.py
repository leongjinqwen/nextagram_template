from flask import Blueprint, render_template,request,url_for,redirect,flash
from models.user import User
from werkzeug.security import generate_password_hash,check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_login import UserMixin,LoginManager,login_required,logout_user,login_user,current_user
from models.image import Image

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')


@users_blueprint.route('/new', methods=['GET'])
def new():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        return render_template('users/new.html')

@users_blueprint.route('/', methods=['POST'])
def create():
    user_password = request.form['password']
    user = User(username=request.form['username'].lower(),email=request.form['email'].lower(),password=user_password)
    if user.save():
        login_user(user)
        flash("Successfully signed up and logged in.","primary")
        return redirect(url_for('index'))
    else:
        return render_template('users/new.html',username=request.form['username'], errors=user.errors)

@users_blueprint.route('/<username>', methods=["GET"])
def show(username):
    user = User.get_or_none(User.username == username)
    if user:
        images = Image.select().where(Image.user==user.id).order_by(Image.created_at.desc())
        ttl = len(images)
        return render_template('users/show.html',user=user,images=images,ttl=ttl)
    return render_template('404.html'), 404

@users_blueprint.route('/search', methods=["POST"])
def search():
    username = request.form['search'].lower()
    return redirect(url_for('users.show',username=username))
    
@users_blueprint.route('/', methods=["GET"])
def index():
    return redirect(url_for('index'))


@users_blueprint.route('/<int:id>/edit', methods=['GET'])
def edit(id):
    try:
        if current_user.id==id or current_user.role =='admin':
            user= User.get(User.id==id)
            return render_template('users/edit.html',user=user)
        return render_template('401.html'), 401    
    except:
        return render_template('401.html'), 401    

@users_blueprint.route('/<int:id>', methods=['POST'])
def update(id):
    if current_user.id==id or current_user.role =='admin':
        user = User.get(User.id == id)
        user_password = request.form['password']
        user.username = request.form['username']
        user.email = request.form['email']
        user.password = user_password
        user.bio = request.form['bio']
        if request.form.get('private'):
            user.private = True
            user.save()
            flash("Successfully updated.","primary")
            return redirect(url_for('users.edit',id=id))
        if not request.form.get('private'):
            user.private = False
            user.save()
            flash("Successfully updated.","primary")
            return redirect(url_for('users.edit',id=id))
        else:
            return render_template('users/edit.html',errors=user.errors,user=user)
    return render_template('401.html'), 401 

