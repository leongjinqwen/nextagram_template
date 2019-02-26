from models.base_model import BaseModel
import peewee as pw
from models.image import Image
from models.user import User


class Donation(BaseModel):
    donor = pw.ForeignKeyField(User, backref='donations')
    amount = pw.DecimalField(decimal_places=2,default=0)
    image = pw.ForeignKeyField(Image, backref='donations')
    
    

    

    