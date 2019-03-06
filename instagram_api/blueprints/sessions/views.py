from flask import Blueprint,jsonify,request

sessions_api_blueprint = Blueprint('sessions_api',
                             __name__,
                             template_folder='templates')

@sessions_api_blueprint.route('/login', methods=['POST'])
def sign_in():
    data = request.get_json()
    auth_token = user.encode
    return 

