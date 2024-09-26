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

def create_component(form_type: str, user_id: int, name: str, ugcid: str) -> bool:
    def string_to_type(class_name):
        return globals()[class_name]
    
    try:
        new_map = string_to_type(form_type)(user_id=user_id, name=name, UGCId=ugcid)
        db.session.add(new_map)
        db.session.commit()
        return True
    except Exception as e:
        return False
    
def verify_compadible(ugcid: str):
    headers = {
    'Accept': 'application/json'
    }
    url = "https://u-24475661.modapi.io/v1/games/3959/mods/"

    # Remove 'UGC' from ID
    ugcid = ugcid[3:]

    try:
        response = requests.get(f'{url}{ugcid}', 
                                params={'api_key': os.getenv('MODIO_API_KEY')}, 
                                headers = headers)
        
        jsonResponse = json.loads(response.content)
        platforms = jsonResponse.get("platforms", False)

        for platform in platforms:
            if 'linux' in platform.values():
                return True
        
        return False

    except Exception as e:
        logger.error(f"Error occured when checking UGC compadibility: {e}")
        return False

if __name__ == "__main__":
    pass