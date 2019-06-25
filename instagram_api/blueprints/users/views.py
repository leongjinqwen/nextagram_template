from flask import Blueprint,jsonify,request,make_response
from models.user import User
from models.image import Image

users_api_blueprint = Blueprint('users_api',
                             __name__,
                             template_folder='templates')

@users_api_blueprint.route('/', methods=['GET'])
def index():
    users = User.select()
    result = []
    for user in users:
        each = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'bio': user.bio,
            'profileImage' : user.profile_image_url,
            'total_images' : len(user.images),
            'fans' : len(user.fans),
            'idols' : len(user.idols)
        }
        result.append(each)
    return jsonify(result)

@users_api_blueprint.route('/new', methods=['POST'])
def create():
    # get the post data
    post_data = request.get_json()

    try:
        new_user = User(
            username=post_data['username'],
            email=post_data['email'].lower(),
            password=post_data['password']
        )

    except:
        responseObject = {
            'status': 'failed',
            'message': ['All fields are required!']
        }

        return make_response(jsonify(responseObject)), 400

    else:

        if not new_user.save():

            responseObject = {
                'status': 'failed',
                'message': new_user.errors
            }

            return make_response(jsonify(responseObject)), 400

        else:
            auth_token = new_user.encode_auth_token(new_user.id)

            responseObject = {
                'status': 'success',
                'message': 'Successfully created a user and signed in.',
                'auth_token': auth_token.decode(),
                'user': {"id": int(new_user.id), "username": new_user.username, "profile_picture": new_user.profile_image_url}
            }

            return make_response(jsonify(responseObject)), 201
    
@users_api_blueprint.route('/feeds', methods=['GET'])
def feeds():
    images =Image.select().order_by(Image.created_at.desc())
    result = []
    for image in images:
        each = {
            'id': image.user.id,
            'image_url': image.image_url,
            'user': image.user.username,
            'created_at': image.created_at,
            'user_profileImage' : image.user.profile_image_url
        }
        result.append(each)
    return jsonify(result)

    
@users_api_blueprint.route('/check_name/<newname>', methods=['GET'])
def check_name(newname):
    result = User.get_or_none(User.username == newname )
    if result == None :
        responseObject = {
            'valid': True,
            'exist': False
        }
        return make_response(jsonify(responseObject)), 201
    
    responseObject = {
        'valid': False,
        'exist': True
    }
    return make_response(jsonify(responseObject)), 400
