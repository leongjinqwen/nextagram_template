from flask import Blueprint, render_template,request,url_for,redirect,flash
from models.user import User
from werkzeug.security import generate_password_hash,check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_login import UserMixin,LoginManager,login_required,logout_user,login_user,current_user
from models.image import Image
from models.fanidol import FanIdol

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
        followed = FanIdol.get_or_none(FanIdol.fan==current_user.id,FanIdol.idol==user.id)
        approved = FanIdol.get_or_none(FanIdol.fan==current_user.id,FanIdol.idol==user.id,FanIdol.approved==True)
        images = Image.select().where(Image.user==user.id).order_by(Image.created_at.desc())
        ttlfans = len(user.fans)
        ttlidols = len(user.idols)
        ttl = len(images)
        return render_template('users/show.html',followed=followed,approved=approved,user=user,images=images,ttl=ttl,ttlfans=ttlfans,ttlidols=ttlidols)
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

@users_blueprint.route('/follow/<int:id>', methods=['POST'])
def follow(id):
    idol = User.get_by_id(id)
    if idol.private == True:
        fan = FanIdol(fan=current_user.id,idol=idol.id,approved=False)
        if fan.save():
            flash(f"Request is sent to {idol.username}. Please wait for approval.","primary")
            return redirect(url_for('index'))
        else:
            flash(f"Unable to send request to {idol.username}. Please try again later.","danger")
            return redirect(url_for('index'))
    else:
        fan = FanIdol(fan=current_user.id,idol=idol.id,approved=True)
        if fan.save():
            flash(f"Successfully followed {idol.username}.","primary")
            return redirect(url_for('index'))
        else:
            flash(f"Failed to follow {idol.username}.","danger")
            return redirect(url_for('index'))

@users_blueprint.route('/unfollow/<int:id>', methods=['POST'])
def unfollow(id):
    idol = User.get_by_id(id)
    fan_status = FanIdol.get(FanIdol.fan==current_user.id,FanIdol.idol==id)
    if idol.private == True:
        if fan_status.approved == True:
            fan = FanIdol.delete().where(FanIdol.fan==current_user.id,FanIdol.idol==idol.id)
            fan.execute()
            flash(f"Successfully unfollowed {idol.username}.","primary")
            return redirect(url_for('index'))
        else:
            fan = FanIdol.delete().where(FanIdol.fan==current_user.id,FanIdol.idol==idol.id)
            fan.execute()
            flash(f"Successfully cancelled your follow request of {idol.username}.","primary")
            return redirect(url_for('users.show_request',id=current_user.id))
    elif idol.private == False:
        fan = FanIdol.delete().where(FanIdol.fan==current_user.id,FanIdol.idol==idol.id)
        fan.execute()
        flash(f"Successfully unfollowed {idol.username}.","primary")
        return redirect(url_for('index'))
    else:
        flash(f"Failed to unfollow {idol.username}. Try again later.","danger")
        return redirect(url_for('index'))


@users_blueprint.route('/<int:id>/follow_request',methods=['GET'])
def show_request(id):
    followers = FanIdol.select().where(FanIdol.idol==id ,FanIdol.approved==False)
    idols = FanIdol.select().where(FanIdol.fan==id, FanIdol.approved==False)
    return render_template('users/follower.html',followers=followers,idols=idols)

@users_blueprint.route('/<int:id>/approved',methods=['POST'])
def approved(id):
    fan = User.get_by_id(id)
    follower = FanIdol.update(approved=True).where(FanIdol.fan==id,FanIdol.idol==current_user.id)
    if follower.execute():
        flash(f'{fan.username} now is your follower.','primary')
        return redirect(url_for('users.show_request',id=current_user.id))
    else:
        flash(f'Failed to approve request,try again later.','danger')
        return redirect(url_for('users.show_request',id=current_user.id))