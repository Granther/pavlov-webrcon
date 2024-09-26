import os
from functools import wraps
import requests
import json

from flask_login import current_user
from flask import redirect, url_for, flash

from logger import create_logger
from models import User
from db_factory import db
from models import User, Map, Mod, GameMode, ModPack, Profile
from forms import SelectProfileForm

logger = create_logger(__name__)

def get_profiles():
    profiles = User.query.filter_by(id=current_user.id).first().profiles
    if not profiles:
        logger.info("Error occured while getting profile, could be [] IDK")
        return []
    
    return profiles

def create_admin():
    admin = User.query.filter_by(id=1000).first()
    if admin:
        logger.info("Admin already exists")
        return 
    
    from app import bcrypt
    password = bcrypt.generate_password_hash(os.getenv("ADMIN_PASSWORD")).decode('utf-8')

    admin = User(id=1000, username="admin", password=password)
    db.session.add(admin)
    db.session.commit()

def admin_authorized(f):
    """Decorator for handling if a user is authorized in regards to login and container access"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))

        if current_user.id != 1000:
            flash("Sorry, you cannot access that page", "danger")
            return redirect(url_for('joke'))
        else:
            # Return original view function
            return f(*args, **kwargs)

    return decorated_function

def create_component(form_type: str, name: str, ugcid: str) -> bool:
    def string_to_type(class_name):
        return globals()[class_name]
    
    try:
        new_map = string_to_type(form_type)(name=name, UGCId=ugcid)
        db.session.add(new_map)
        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"Error occured while creating component: {e}")
        return False
    
def verify_UGC(ugcid: str):
    if ugcid[:3] != 'UGC':
        print(ugcid[:2])
        return False
    
    return ugcid[3:]
    
def verify_compadible(ugcid: str, modtype: str):
    headers = {
    'Accept': 'application/json'
    }
    url = "https://u-24475661.modapi.io/v1/games/3959/mods/"

    # Remove 'UGC' from ID
    ugcid = verify_UGC(ugcid)
    if not ugcid:
        return False, "ID must include 'UGC' at the beginning, boomer, like so, UGC4206969"

    try:
        response = requests.get(f'{url}{ugcid}', 
                                params={'api_key': os.getenv('MODIO_API_KEY')}, 
                                headers = headers)
        json_response = json.loads(response.content)

        metadata_blob = json.loads(json_response.get("metadata_blob"))
        json_modtype = dict(metadata_blob).get('ModType')

        # if json_modtype.lower() != modtype:
        #     return False, f"ID entered is not a {modtype}, but actually a {json_modtype}"
        
        platforms = json_response.get("platforms", False)
        for platform in platforms:
            if 'linux' in platform.values():
                return True, None
        
        return False, f"This {modtype} is not compadible with the server (Linux)"

    except Exception as e:
        logger.error(f"Error occured when checking UGC compadibility: {e}")
        return False, f"Unknown error occured while checking mod compat, please verify the ID and format"

def get_mod_url(ugcid: str):
    headers = {
    'Accept': 'application/json'
    }
    url = f"https://u-24475661.modapi.io/v1/games/3959/mods/"

    ugcid = verify_UGC(ugcid)
    if not ugcid:
        logger.error("Not able to verify integrity of UGCID while getting URL")
        return None

    try:
        response = requests.get(f'{url}{ugcid}', 
                                params={'api_key': os.getenv('MODIO_API_KEY')}, 
                                headers = headers)
        json_response = json.loads(response.content)

        return json_response.get('profile_url')

    except Exception as e:
        logger.error(f"Error occured while getting mod URL: {e}")
        return None

def create_profile_select_form():
    form = SelectProfileForm()
    profiles = Profile.query.all()
    form.profiles.choices = [(profile.id, profile.name) for profile in profiles]
    return form

if __name__ == "__main__":
    get_mod_url("2803451")