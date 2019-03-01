import os
import config
from flask import Flask,render_template,request,url_for,redirect,flash,escape
from models.base_model import db
from flask_wtf.csrf import CSRFProtect
import braintree
from redis import Redis
from rq import Queue

redis_conn = Redis()
q = Queue(connection=redis_conn)

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=os.environ.get("BT_MERCHANT_ID"),
        public_key=os.environ.get("BT_PUBLIC_KEY"),
        private_key=os.environ.get("BT_PRIVATE_KEY")
    )
)
def generate_client_token():
    return gateway.client_token.generate()

def transact(options):
    return gateway.transaction.sale(options)

def find_transaction(id):
    return gateway.transaction.find(id)
    
web_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'instagram_web')

app = Flask('NEXTAGRAM', root_path=web_dir)
csrf = CSRFProtect(app)

if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

@app.before_request
def before_request():
    db.connect()

@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        print(db)
        print(db.close())
    return exc

from flask_login import current_user,login_required
from models.fanidol import FanIdol
from models.user import User
from models.image import Image
@app.route('/')
@login_required
# feed should include my idols post and my own photo
def index():
    idols = FanIdol.select(FanIdol.idol).where(FanIdol.fan==current_user.id,FanIdol.approved==True)
    images =Image.select().where((Image.user.in_(idols)) | (Image.user==current_user.id)).order_by(Image.created_at.desc())
    return render_template('home.html',images=images)

@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

