from models.base_model import BaseModel
import peewee as pw
from models.user import User


class Images(BaseModel):
    gallery = pw.CharField(unique=True,null=False)
    user = pw.ForeignKeyField(User, backref='users')

    
    
    

    