from db_factory import db
from flask_login import UserMixin
import uuid

def generate_uuid():
    return str(uuid.uuid4())

modpack_mod_association = db.Table('modpack_mod_association',
    db.Column('modpack_id', db.Integer, db.ForeignKey('mod_pack.id'), primary_key=True),
    db.Column('mod_id', db.Integer, db.ForeignKey('mod.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    profiles = db.relationship('Profile', backref='user', lazy=True)

class Map(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    name = db.Column(db.String, nullable=False)
    UGCId = db.Column(db.String, nullable=False)

    def __str__(self):
        return self.name

class GameMode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    name = db.Column(db.String, nullable=False)
    UGCId = db.Column(db.String, nullable=False)

    def __str__(self):
        return self.name

class Mod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    modpack_id = db.Column(db.Integer, db.ForeignKey('mod_pack.id'))
    name = db.Column(db.String, nullable=False)
    UGCId = db.Column(db.String, nullable=False)
    modpacks = db.relationship("ModPack", secondary=modpack_mod_association, backref="mods")

    # This is what happens when these are displayed
    def __str__(self):
        return self.name

class ModPack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    name = db.Column(db.String, nullable=False)
    # mods = db.relationship('Mod', backref='mod_pack', lazy=True)

    def __str__(self):
        return self.name

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    name = db.Column(db.String, nullable=False)

    map_id = db.Column(db.Integer, db.ForeignKey('map.id'), nullable=True)
    map = db.relationship('Map', backref='profile', uselist=False)
    
    gamemode_id = db.Column(db.Integer, db.ForeignKey('game_mode.id'), nullable=True)
    gamemode = db.relationship('GameMode', backref='profile', uselist=False)
    
    modpack_id = db.Column(db.Integer, db.ForeignKey('mod_pack.id'), nullable=True)
    modpack = db.relationship('ModPack', backref='profile', uselist=False)

    def __str__(self):
        return self.name

# class Rotation(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     created = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
#     profiles = db.relationship('Profile', backref='rotation', lazy=True)