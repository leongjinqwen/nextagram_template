import os
from app import app
from flask import render_template
from flask_assets import Environment, Bundle
from .util.assets import bundles
import sendgrid
from instagram_web.util.google_oauth import oauth

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))

oauth.init_app(app)
assets = Environment(app)
assets.register(bundles)


from instagram_web.blueprints.users.views import users_blueprint
from instagram_web.blueprints.images.views import images_blueprint
from instagram_web.blueprints.sessions.views import sessions_blueprint
from instagram_web.blueprints.checkouts.views import checkouts_blueprint
app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(images_blueprint, url_prefix="/images")
app.register_blueprint(sessions_blueprint, url_prefix="/sessions")
app.register_blueprint(checkouts_blueprint, url_prefix="/checkouts")

from models.image import Image
from flask_login import current_user
from models.fanidol import FanIdol
@app.route('/')
# feed should include my idols post and my own photo
def index():
    if current_user.is_authenticated:
        idols = FanIdol.select(FanIdol.idol).where(FanIdol.fan==current_user.id,FanIdol.approved==True)
        images =Image.select().where((Image.user.in_(idols)) | (Image.user==current_user.id)).order_by(Image.created_at.desc())
        return render_template('home.html',images=images)
    else:
        return render_template('sessions/new.html')
        
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route("/")
def home():
    return render_template('home.html')
