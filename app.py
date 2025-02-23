import os

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file, copy_current_request_context
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

from db_factory import db
from models import User, Map, Mod, GameMode, ModPack, Profile
from forms import LoginForm, RegisterForm, AddProfileRotationForm, NewGamemodeForm, NewModForm, NewMapForm, ModPackForm, NewProfileForm, RotateButton, SelectProfileForm, NewItemForm
from logger import create_logger
from pavrcon import set_profile, rotate_map, server_status
from utils import create_component, create_admin, get_profiles, admin_authorized, verify_compadible, create_profile_select_form, get_mod_url, seed_data, get_mod_field

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

current_profile = None

with app.app_context():
    db.create_all()
    seed_data()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/", methods=['POST', 'GET'])
def index():
    new_item_form = NewItemForm()

    mods = Mod.query.all()
    maps = Map.query.all()
    gamemodes = GameMode.query.all()
    modpacks = ModPack.query.all()
    profiles = Profile.query.all()

    status = server_status()
    player_count = status['PlayerCount']
    map_name = status['MapName']
    gamemode_name = status['GameMode']

    #logger.debug(f"uiqhiheiuqe: {current_profile}")

    #curr_profile_gamemode = current_profile.gamemode.name
    #curr_profile_map = current_profile.map.name
    #curr_profile_modpack = url_for("modpack", current_profile.mod.id)

    #return render_template("home.html", map_form=map_form, mods=mods, maps=maps, gamemodes=gamemodes, modpacks=modpacks,
    return render_template("home.html", mods=mods, maps=maps, gamemodes=gamemodes, modpacks=modpacks, profiles=profiles, new_item_form=new_item_form, player_count=player_count, map_name=map_name, gamemode_name=gamemode_name)
                           #curr_profile_gamemode=curr_profile_gamemode, curr_profile_map=curr_profile_map)

@app.route("/init_admin", methods=['POST', 'GET'])
def init_admin():
    create_admin()
    return redirect(url_for('index'))

@app.route("/new_item", methods=["POST", "GET"])
def new_item():
    new_item_form = NewItemForm()

    if new_item_form.validate_on_submit():
        item_type_name = new_item_form.type.data

        ug_name = get_mod_field(ugcid=new_item_form.id.data, field_name='name')
        logger.debug(f"name: {ug_name}")

        result, msg = verify_compadible(new_item_form.id.data, modtype=item_type_name.lower())
        if not result:
            flash(msg)
            return redirect(url_for('index'))
        
        res = create_component(form_type=item_type_name, name=new_item_form.name.data, ugcid=new_item_form.id.data)
        if not res:
            flash(f"Error creating new {new_item_form.type.data} entry")
            return redirect(url_for('index'))
        
        flash(f"Successfully created new {new_item_form.type.data} entry")
        logger.debug(f"Created new {item_type_name} {new_item_form.name.data}")
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
        logger.debug(form.map.data)

        new_profile.map = form.map.data
        new_profile.modpack = form.modpack.data
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

@app.route("/query_ugc", methods=['POST'])
def query_ugc():
    data = request.json
    ugcid = data['ugc']
    logger.debug(ugcid)
    ug_name = get_mod_field(ugcid=str(ugcid), field_name='name')
    logger.debug(ug_name)
    return jsonify({"title": ug_name})

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
            logger.debug(form.profiles.data)
            profile = Profile.query.get(form.profiles.data)
            mods = []
            for mod in profile.modpack.mods:
                mods.append(mod.UGCId)

            if not set_profile(map_id=profile.map.UGCId, gamemode_id=profile.gamemode.UGCId, mods=mods):
                logger.fatal(f"Failed to set profile {profile.id} {profile.name}")
                raise RuntimeError

            current_profile = profile
            logger.debug(f"Set new profile: {profile}")
            
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

@app.route("/modpack/edit/<int:id>", methods=['GET', 'POST'])
def edit_modpack(id):
    modpack = ModPack.query.get(id)
    form = ModPackForm(data={"mods": modpack.mods, "name": modpack.name})
    form.mods.query = Mod.query.all()

    if form.validate_on_submit():
        modpack.name = form.name.data
        modpack.mods.clear()
        modpack.mods.extend(form.mods.data)
        db.session.add(modpack)
        db.session.commit()

        return redirect(url_for('index'))
    
    return render_template("new_modpack.html", form=form)

@app.route("/modpack/delete/<int:id>", methods=['POST', 'GET'])
@admin_authorized
def delete_modpack(id):
    modpack = ModPack.query.get(id)
    if modpack:
        db.session.delete(modpack)
        db.session.commit()
        logger.info(f"Deleted modpack of id: {id}")

    return redirect(url_for('index'))

@app.route("/profile/edit/<int:id>", methods=['GET', 'POST'])
def edit_profile(id):
    profile = Profile.query.get(id)
    form = NewProfileForm(data={"modpack": profile.modpack, "map": profile.map, "gamemode": profile.gamemode, "name": profile.name})
    form.modpack.query = ModPack.query.all()
    form.map.query = Map.query.all()
    form.gamemode.query = GameMode.query.all()

    if form.validate_on_submit():   
        profile.name = form.name.data     
        profile.map = form.map.data
        profile.modpack = form.modpack.data
        profile.gamemode = form.gamemode.data

        db.session.commit()

        return redirect(url_for('index'))
    
    return render_template("new_profile.html", form=form)

@app.route("/profile/delete/<int:id>", methods=['POST', 'GET'])
@admin_authorized
def delete_profile(id):
    profile = Profile.query.get(id)
    if profile:
        db.session.delete(profile)
        db.session.commit()
        logger.info(f"Deleted profile of id: {id}")

    return redirect(url_for('index'))

@app.route("/profile/<int:id>", methods=['GET'])
def profile(id):
    if current_user.is_authenticated:
        logger.debug("Admin is logged in")
    profile = Profile.query.filter_by(id=id).first()

    return render_template("profile.html", profile=profile)

@app.route("/delete/<ugc_type>/<ugcid>")
def delete_component(ugc_type, ugcid):
    if ugc_type == "Mod":
        comp = Mod.query.filter_by(UGCId=ugcid).first()
    elif ugc_type == "Gamemode":
        comp = GameMode.query.filter_by(UGCId=ugcid).first()
    elif ugc_type == "Map":
        comp = Map.query.filter_by(UGCId=ugcid).first()
    else:
        logger.error(f"Attempted to delete component of type: {ugc_type} with UGCId of {ugcid} but did not find type...")
        return redirect(url_for('index'))
    
    db.session.delete(comp)
    db.session.commit()
    logger.debug(f"Deleting component of type: {ugc_type} with UGCId of {ugcid}")
    
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
