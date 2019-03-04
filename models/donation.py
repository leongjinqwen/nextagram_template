from models.base_model import BaseModel
import peewee as pw
from models.image import Image
from models.user import User


class Donation(BaseModel):
    donor_id = pw.ForeignKeyField(User, backref='donations')
    amount = pw.DecimalField(decimal_places=2,default=0)
    image_id = pw.ForeignKeyField(Image, backref='donations')
    
    

    

    