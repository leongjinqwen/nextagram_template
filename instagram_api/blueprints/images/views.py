from flask import Blueprint,jsonify
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

