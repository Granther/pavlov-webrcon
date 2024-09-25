from db_factory import db
from flask_login import UserMixin
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    containers = db.relationship('Containers', backref='users', lazy=True)

class Map(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    UGCId = db.Column(db.String, nullable=False)

class GameMode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    UGCId = db.Column(db.String, nullable=False)

class Mod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    UGCId = db.Column(db.String, nullable=False)

class ModPack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    name = db.Column(db.String, nullable=False)
    mods = db.relationship('Mods', backref='mod_pack', lazy=True)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    name = db.Column(db.String, nullable=False)
    mod_packs = db.relationship('ModPack', backref='profile', lazy=True)
    gamemode = db.relationship('GameMode', backref='profile', lazy=True)
    map = db.relationship('Map', backref='profile', lazy=True)



