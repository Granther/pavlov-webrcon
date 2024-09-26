import os
from collections import defaultdict
from uuid import uuid4

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file, copy_current_request_context
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, join_room
from flask_cors import CORS
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

from db_factory import db
from models import User, Map, Mod, GameMode, ModPack, Profile
from forms import LoginForm, RegisterForm, AddProfileRotationForm, NewGamemodeForm, NewModForm, NewMapForm, NewModpackForm, ModPackForm, NewProfileForm
from logger import create_logger
from pavrcon import set_profile, rotate_map

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "backup-key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///backup.db")

db.init_app(app)
bcrypt = Bcrypt(app)
CORS(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = None
login_manager.login_message_category = 'info'

logger = create_logger(__name__)

with app.app_context():
    db.create_all()

def get_profiles():
    profiles = User.query.filter_by(id=current_user.id).first().profiles
    if not profiles:
        logger.info("Error occured while getting profile, could be [] IDK")
        return []
    
    return profiles

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home", methods=['POST', 'GET'])
@login_required
def home():
    map_form = NewMapForm()
    gamemode_form = NewGamemodeForm()
    mod_form = NewModForm()

    profiles = get_profiles()

    return render_template("home.html", map_form=map_form, 
                           gamemode_form=gamemode_form, mod_form=mod_form, profiles=profiles)

@app.route("/new_map", methods=['POST', 'GET'])
def new_map():
    map_form = NewMapForm()
    gamemode_form = NewGamemodeForm()
    mod_form = NewModForm()

    if map_form.validate_on_submit():
        res = create(form_type="Map", user_id=current_user.id, name=map_form.name.data, ugcid=map_form.id.data)
        if not res:
            flash("Error creating new map entry")
            return redirect(url_for('error'))
        
        flash("Successfully created new map entry")
        logger.debug(f"Create new map {map_form.name.data}")
        return redirect(url_for('home'))
    
    return redirect(url_for('index'))

@app.route("/new_gamemode", methods=['POST', 'GET'])
def new_gamemode():
    map_form = NewMapForm()
    gamemode_form = NewGamemodeForm()
    mod_form = NewModForm()

    if gamemode_form.validate_on_submit():
        res = create(form_type="GameMode", user_id=current_user.id, name=gamemode_form.name.data, ugcid=gamemode_form.id.data)
        if not res:
            flash("Error creating new gamemode entry")
            return redirect(url_for('error'))
        
        flash("Successfully created new gamemode entry")
        logger.debug(f"Create new gamemode {gamemode_form.name.data}")
        return redirect(url_for('home'))

    return redirect(url_for('index'))

@app.route("/new_mod", methods=['POST', 'GET'])
def new_mod():
    map_form = NewMapForm()
    gamemode_form = NewGamemodeForm()
    mod_form = NewModForm()

    if mod_form.validate_on_submit():
        res = create(form_type="Mod", user_id=current_user.id, name=mod_form.name.data, ugcid=mod_form.id.data)
        if not res:
            flash("Error creating new mod entry")
            return redirect(url_for('error'))
        
        flash("Successfully created new mod entry")
        logger.debug(f"Create new mod {mod_form.name.data}")
        return redirect(url_for('home'))

    return redirect(url_for('index'))

def create(form_type: str, user_id: int, name: str, ugcid: str) -> bool:
    def string_to_type(class_name):
        return globals()[class_name]
    
    try:
        new_map = string_to_type(form_type)(user_id=user_id, name=name, UGCId=ugcid)
        db.session.add(new_map)
        db.session.commit()
        return True
    except Exception as e:
        return False
    
@app.route("/new_modpack", methods=['GET', 'POST'])
def new_modpack():
    form = ModPackForm()
    form.mods.query = Mod.query.all()

    if form.validate_on_submit():
        selected_mods = form.mods.data 
        mod_pack = ModPack(user_id=current_user.id, name=form.name.data)
        mod_pack.mods.clear()
        mod_pack.mods.extend(selected_mods)
        db.session.add(mod_pack)
        db.session.commit()

        return redirect(url_for('home'))
    
    return render_template("new_modpack.html", form=form)

@app.route("/new_profile", methods=['GET', 'POST'])
def new_profile():
    form = NewProfileForm()
    form.modpack.query = ModPack.query.all()
    form.map.query = Map.query.all()
    form.gamemode.query = GameMode.query.all()

    if form.validate_on_submit():
        new_profile = Profile(user_id=current_user.id, name=form.name.data)
        
        logger.debug(form.modpack.data)

        new_profile.modpack = form.modpack.data
        new_profile.map = form.map.data
        new_profile.gamemode = form.gamemode.data

        db.session.add(new_profile)
        db.session.commit()

        return redirect(url_for('home'))
    
    return render_template("new_profile.html", form=form)

@app.route("/profile/<int:id>", methods=['POST', 'GET'])
def profile(id):
    profile = Profile.query.filter_by(id=id).first()

    return render_template("profile.html", profile=profile)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        username = User.query.filter_by(username=form.username.data).first()
        if username:
            flash('Register Unsuccessful. Username already associated with account', 'danger')
            return render_template("register.html", title='Register', form=form)

        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/error")
def error():
    return render_template("error.html")

@app.route("/admin", methods=['POST', 'GET'])
@login_required
def admin():
    form = AddProfileRotationForm()
    profiles = get_profiles()

    if form.validate_on_submit():
        try:
            profile = Profile.query.get(form.profileid.data)

            mods = []
            for mod in profile.modpack.mods:
                mods.append(mod.UGCId)

            if not set_profile(map_id=profile.map.id, gamemode_id=profile.gamemode.id, mods=mods):
                logger.fatal(f"Failed to set profile {profile.id} {profile.name}")
                raise RuntimeError
            
        except RuntimeError as e:
            flash(f"Failed to set profile: {e}")
            return redirect(url_for('admin'))
        
        flash(f"Successfully set profile")
        return redirect(url_for('admin'))

    return render_template("admin.html", title="Admin Panel", form=form, profiles=profiles)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)