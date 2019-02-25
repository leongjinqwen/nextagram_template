from models.base_model import BaseModel
import peewee as pw
from models.user import User
from playhouse.hybrid import hybrid_property
from app import app



class Image(BaseModel):
    name = pw.CharField()
    image_path = pw.TextField(unique=True,null=False)
    user = pw.ForeignKeyField(User, backref='images')
    gallery = pw.BooleanField(default=True)

    @hybrid_property
    def image_url(self):
        return app.config['AWS_S3_DOMAIN'] + self.image_path
    

    