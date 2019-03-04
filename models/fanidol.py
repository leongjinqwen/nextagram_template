from models.base_model import BaseModel
from models.user import User
import peewee as pw
from flask_login import current_user

class FanIdol(BaseModel):
    fan_id = pw.ForeignKeyField(User, backref='idols')
    idol_id = pw.ForeignKeyField(User, backref='fans')
    approved= pw.BooleanField(default=False)