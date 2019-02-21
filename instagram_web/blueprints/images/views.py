from app import app
from flask import Blueprint, render_template,request,url_for,redirect,flash
from flask_login import current_user
from helpers import s3
from werkzeug.utils import secure_filename
import datetime
from models.image import Image

images_blueprint = Blueprint('images',
                            __name__,
                            template_folder='templates/images')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def upload_file_to_s3(file, bucket_name, acl="public-read"):
    u_name = current_user.id + file.filename + datetime.datetime.now()
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
    return u_name

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@images_blueprint.route('/<int:id>/upload',methods=["POST"])
def upload(id):
    if "user_file" not in request.files:
        return "No user_file key in request.files"
    file = request.files["user_file"]
    if file.filename == "":
        return "Please select a file"
    if file and allowed_file(file.filename):
        file.filename = secure_filename(file.filename)
        output = upload_file_to_s3(file, app.config["S3_BUCKET"])
        image = Image(image_path = str(output),user_id = current_user.id)
        if image.save():
            flash("Successfully saved.")
            return redirect(url_for('users.edit',id=id))
    else:
        return render_template('home.html')