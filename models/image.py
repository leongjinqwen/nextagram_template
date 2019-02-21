from models.base_model import BaseModel
import peewee as pw
from models.user import User
from playhouse.hybrid import hybrid_property
from app import app



class Image(BaseModel):
    image_path = pw.TextField(unique=True,null=False)
    user_id = pw.ForeignKeyField(User, backref='users')

    
    @hybrid_property
    def profile_image_url(self):
        return app.config['AWS_S3_DOMAIN'] + self.image_path
    

    