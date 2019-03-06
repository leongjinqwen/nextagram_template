from flask import Blueprint,jsonify
from models.user import User

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
         'profileImage' : user.profile_image_url
      }
      result.append(each)
   return jsonify(result)
    