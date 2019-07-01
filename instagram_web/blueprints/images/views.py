from app import app
from flask import Blueprint, render_template,request,url_for,redirect,flash
from flask_login import current_user
from instagram_web.util.helpers import upload_file_to_s3
from models.image import Image
from models.user import User
from playhouse.flask_utils import object_list

images_blueprint = Blueprint('images',
                            __name__,
                            template_folder='templates')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@images_blueprint.route('/',methods=["GET"])
def index():
    images = Image.select().where(Image.user==current_user.id).order_by(Image.created_at.desc())
    return object_list('images/show.html',query=images,paginate_by=10)

@images_blueprint.route('/<int:id>/upload',methods=["POST"])
def upload(id):
    if "user_file" not in request.files:
        flash("No user_file key in request.files",'danger')
        return redirect(url_for('index'))
    file = request.files["user_file"]
    if file.filename == "":
        flash("Please select a file",'danger')
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        output = upload_file_to_s3(file)
        if request.form.get('gallery'):
            gallery_checked = False
            image = Image(name=file.filename ,image_path = str(output),user = current_user.id, gallery=gallery_checked)
            if image.save():
                flash("Your profile photo successfully uploaded.",'primary')
                User.update(profile_pic =str(output) ).where(User.id==id).execute()
                return redirect(url_for('index'))
            return render_template('home.html')
        else:
            image = Image(name=file.filename ,image_path = str(output),user = current_user.id, gallery=True)
            if image.save():
                flash("Photo successfully uploaded.",'primary')
                return redirect(url_for('index'))
    else:
        return render_template('home.html')

@images_blueprint.route('/<int:id>/delete',methods=["POST"])
def delete(id):
    if Image.delete_by_id(id):
        flash("Photo successfully removed from your profile.",'primary')
        return redirect(url_for('users.show',username=current_user.username))
    else:
        flash('Unable to remove photo from your profile.','danger')
        return render_template('users/show.html',username=current_user.username)

@images_blueprint.route('/<int:id>/edit',methods=["POST"])
def update(id):
    image = Image.get_by_id(id)
    if image.gallery == True:
        image.gallery = False
        image.save()
        User.update(profile_pic=image.image_path).where(User.id==current_user.id).execute()
        flash("Your profile photo successfully updated.",'primary')
        return redirect(url_for('users.show',username=current_user.username))
    else:
        image.gallery = True
        image.save()
        flash('Successfully remove photo from profile picture album.','primary')
        return redirect(url_for('users.show',username=current_user.username))
    