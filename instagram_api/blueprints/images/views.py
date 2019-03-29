from flask import Blueprint,jsonify,request,make_response
from models.user import User
from models.image import Image

images_api_blueprint = Blueprint('images_api',
                             __name__,
                             template_folder='templates')

@images_api_blueprint.route('/<int:id>', methods=['GET'])
def index(id):
    images = Image.select().where(Image.user==id)
    result = []
    for image in images:
        result.append(image.image_url)
    return jsonify(result)

@images_api_blueprint.route('/me', methods=['GET'])
def show():
    auth_header = request.headers.get('Authorization')

    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        responseObject = {
            'status': 'failed',
            'message': 'No authorization header found'
        }

        return make_response(jsonify(responseObject)), 401

    user_id = User.decode_auth_token(auth_token)

    user = User.get_or_none(id=user_id)

    if user:
        images = Image.select().where(Image.user_id == user.id)
        images = [image.image_url for image in images]

        return jsonify(images)
    else:
        responseObject = {
            'status': 'failed',
            'message': 'Authentication failed'
        }

        return make_response(jsonify(responseObject)), 401