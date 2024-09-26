import os

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file, copy_current_request_context
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

from db_factory import db
from models import User, Map, Mod, GameMode, ModPack, Profile
from forms import LoginForm, RegisterForm, AddProfileRotationForm, NewGamemodeForm, NewModForm, NewMapForm, NewModpackForm, ModPackForm, NewProfileForm, RotateButton
from logger import create_logger
from pavrcon import set_profile, rotate_map
from utils import create_component, create_admin, get_profiles, admin_authorized

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
@login_required
def index():
    map_form = NewMapForm()
    gamemode_form = NewGamemodeForm()
    mod_form = NewModForm()

    profiles = get_profiles()

    return render_template("home.html", map_form=map_form, 
                           gamemode_form=gamemode_form, mod_form=mod_form, profiles=profiles)

@app.route("/init_admin", methods=['POST', 'GET'])
def init_admin():
    create_admin()
    return redirect(url_for('index'))

@app.route("/new_map", methods=['POST', 'GET'])
@login_required
def new_map():
    map_form = NewMapForm()

    if map_form.validate_on_submit():
        res = create_component(form_type="Map", user_id=current_user.id, name=map_form.name.data, ugcid=map_form.id.data)
        if not res:
            flash("Error creating new map entry")
            return redirect(url_for('error'))
        
        flash("Successfully created new map entry")
        logger.debug(f"Create new map {map_form.name.data}")
        return redirect(url_for('home'))
    
    return redirect(url_for('index'))

@app.route("/new_gamemode", methods=['POST', 'GET'])
@login_required
def new_gamemode():
    gamemode_form = NewGamemodeForm()

    if gamemode_form.validate_on_submit():
        res = create_component(form_type="GameMode", user_id=current_user.id, name=gamemode_form.name.data, ugcid=gamemode_form.id.data)
        if not res:
            flash("Error creating new gamemode entry")
            return redirect(url_for('error'))
        
        flash("Successfully created new gamemode entry")
        logger.debug(f"Create new gamemode {gamemode_form.name.data}")
        return redirect(url_for('home'))

    return redirect(url_for('index'))

@app.route("/new_mod", methods=['POST', 'GET'])
@login_required
def new_mod():
    mod_form = NewModForm()

    if mod_form.validate_on_submit():
        res = create_component(form_type="Mod", user_id=current_user.id, name=mod_form.name.data, ugcid=mod_form.id.data)
        if not res:
            flash("Error creating new mod entry")
            return redirect(url_for('error'))
        
        flash("Successfully created new mod entry")
        logger.debug(f"Create new mod {mod_form.name.data}")
        return redirect(url_for('home'))

    return redirect(url_for('index'))
    
@app.route("/new_modpack", methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
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
    set_profile_form = AddProfileRotationForm()
    rotate_form = RotateButton()
    profiles = get_profiles()

    return render_template("admin.html", rotate_form=rotate_form, set_profile_form=set_profile_form, profiles=profiles)

@app.route("/admin_set_profile", methods=['POST', 'GET'])
@admin_authorized
def admin_set_profile():
    form = AddProfileRotationForm()

    if form.validate_on_submit():
        try:
            profile = Profile.query.get(form.profileid.data)
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)