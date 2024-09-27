import os

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file, copy_current_request_context
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

from db_factory import db
from models import User, Map, Mod, GameMode, ModPack, Profile
from forms import LoginForm, RegisterForm, AddProfileRotationForm, NewGamemodeForm, NewModForm, NewMapForm, ModPackForm, NewProfileForm, RotateButton, SelectProfileForm
from logger import create_logger
from pavrcon import set_profile, rotate_map
from utils import create_component, create_admin, get_profiles, admin_authorized, verify_compadible, create_profile_select_form, get_mod_url

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "backup-key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///backup.db")

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/", methods=['POST', 'GET'])
def index():
    map_form = NewMapForm()
    gamemode_form = NewGamemodeForm()
    mod_form = NewModForm()

    mods = Mod.query.all()
    maps = Map.query.all()
    gamemodes = GameMode.query.all()
    modpacks = ModPack.query.all()
    profiles = Profile.query.all()

    return render_template("home.html", map_form=map_form, mods=mods, maps=maps, gamemodes=gamemodes, modpacks=modpacks,
                           gamemode_form=gamemode_form, mod_form=mod_form, profiles=profiles)

@app.route("/init_admin", methods=['POST', 'GET'])
def init_admin():
    create_admin()
    return redirect(url_for('index'))

@app.route("/new_map", methods=['POST', 'GET'])
def new_map():
    map_form = NewMapForm()

    if map_form.validate_on_submit():
        result, msg = verify_compadible(map_form.id.data, modtype='map') 
        if not result:
            flash(msg)
            return redirect(url_for('index'))
    
        res = create_component(form_type="Map", name=map_form.name.data, ugcid=map_form.id.data)
        if not res:
            flash("Error creating new map entry")
            return redirect(url_for('index'))
        
        flash("Successfully created new map entry")
        logger.debug(f"Create new map {map_form.name.data}")
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))

@app.route("/new_gamemode", methods=['POST', 'GET'])
def new_gamemode():
    gamemode_form = NewGamemodeForm()

    if gamemode_form.validate_on_submit():
        result, msg = verify_compadible(gamemode_form.id.data, modtype='gamemode') 
        if not result:
            flash(msg)
            return redirect(url_for('index'))
        
        res = create_component(form_type="GameMode", name=gamemode_form.name.data, ugcid=gamemode_form.id.data)
        if not res:
            flash("Error creating new gamemode entry")
            return redirect(url_for('index'))
        
        flash("Successfully created new gamemode entry")
        logger.debug(f"Create new gamemode {gamemode_form.name.data}")
        return redirect(url_for('index'))

    return redirect(url_for('index'))

@app.route("/new_mod", methods=['POST', 'GET'])
def new_mod():
    mod_form = NewModForm()

    if mod_form.validate_on_submit():
        result, msg = verify_compadible(mod_form.id.data, modtype='mod') 
        if not result:
            flash(msg)
            return redirect(url_for('index'))

        res = create_component(form_type="Mod", name=mod_form.name.data, ugcid=mod_form.id.data)
        if not res:
            flash("Error creating new mod entry")
            return redirect(url_for('index'))
        
        flash("Successfully created new mod entry")
        logger.debug(f"Create new mod {mod_form.name.data}")
        return redirect(url_for('index'))

    return redirect(url_for('index'))
    
@app.route("/new_modpack", methods=['GET', 'POST'])
def new_modpack():
    form = ModPackForm()
    form.mods.query = Mod.query.all()

    if form.validate_on_submit():
        selected_mods = form.mods.data 
        mod_pack = ModPack(name=form.name.data)
        mod_pack.mods.clear()
        mod_pack.mods.extend(selected_mods)
        db.session.add(mod_pack)
        db.session.commit()

        return redirect(url_for('index'))
    
    return render_template("new_modpack.html", form=form)

@app.route("/new_profile", methods=['GET', 'POST'])
def new_profile():
    form = NewProfileForm()
    form.modpack.query = ModPack.query.all()
    form.map.query = Map.query.all()
    form.gamemode.query = GameMode.query.all()

    if form.validate_on_submit():
        new_profile = Profile(name=form.name.data)
        
        logger.debug(form.modpack.data)

        new_profile.modpack = form.modpack.data
        new_profile.map = form.map.data
        new_profile.gamemode = form.gamemode.data

        db.session.add(new_profile)
        db.session.commit()

        return redirect(url_for('index'))
    
    return render_template("new_profile.html", form=form)

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

@app.route("/boomer")
def boomer():
    return render_template("boomer.html")

@app.route("/register", methods=['GET', 'POST'])
@admin_authorized
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
    return render_template('register.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/error")
def error():
    return render_template("error.html")

@app.route("/admin", methods=['POST', 'GET'])
@admin_authorized
def admin():
    set_profile_form = create_profile_select_form()
    rotate_form = RotateButton()
    profiles = Profile.query.all()

    return render_template("admin.html", rotate_form=rotate_form, set_profile_form=set_profile_form, profiles=profiles)

@app.route("/admin_set_profile", methods=['POST', 'GET'])
@admin_authorized
def admin_set_profile():
    form = create_profile_select_form()

    if form.validate_on_submit():
        try:
            profile = Profile.query.get(form.profiles.data)
            mods = []
            for mod in profile.modpack.mods:
                mods.append(mod.UGCId)

            if not set_profile(map_id=profile.map.UGCId, gamemode_id=profile.gamemode.UGCId, mods=mods):
                logger.fatal(f"Failed to set profile {profile.id} {profile.name}")
                raise RuntimeError
            
        except RuntimeError as e:
            flash(f"Failed to set profile: {e}")
            return redirect(url_for('admin'))
        
        flash(f"Successfully set profile")
        return redirect(url_for('admin'))

    return redirect(url_for('admin'))

@app.route("/admin_rotate_map", methods=['POST', 'GET'])
@admin_authorized
def admin_rotate_map():
    form = RotateButton()

    if form.validate_on_submit():
        try:
            if not rotate_map():
                logger.fatal(f"Failed to rotate server")
                raise RuntimeError
            
        except RuntimeError as e:
            flash(f"Failed to rotate server {e}")
            return redirect(url_for('admin'))
        
        flash(f"Successfully rotated server")
        return redirect(url_for('admin'))

    return redirect(url_for('admin'))

@app.route("/joke", methods=['GET'])
def joke():
    return render_template("joke.html")

@app.route("/mod/<int:id>", methods=['GET'])
def mod(id):
    mod = Mod.query.filter_by(id=id).first()
    modio_url = get_mod_url(mod.UGCId)

    return render_template("component.html", component=mod, type="Mod", modio_url=modio_url)

@app.route("/gamemode/<int:id>", methods=['GET'])
def gamemode(id):
    gamemode = GameMode.query.filter_by(id=id).first()
    modio_url = get_mod_url(gamemode.UGCId)

    return render_template("component.html", component=gamemode, type="Gamemode", modio_url=modio_url)

@app.route("/map/<int:id>", methods=['GET'])
def map(id):
    map = Map.query.filter_by(id=id).first()
    modio_url = get_mod_url(map.UGCId)

    return render_template("component.html", component=map, type="Map", modio_url=modio_url)

@app.route("/modpack/<int:id>", methods=['GET'])
def modpack(id):
    modpack = ModPack.query.filter_by(id=id).first()

    return render_template("modpack.html", modpack=modpack)

@app.route("/profile/<int:id>", methods=['GET'])
def profile(id):
    profile = Profile.query.filter_by(id=id).first()

    return render_template("profile.html", profile=profile)

if __name__ == "__main__":
    app.run(debug=True)