from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms_sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from models import Mod

class ModPackForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    mods = QuerySelectMultipleField("Mods")
    submit = SubmitField('Create Mod Pack', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-black py-2 px-5 rounded-full font-bold text-md transition duration-300"})

class NewProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    map = QuerySelectField("Maps")
    gamemode = QuerySelectField("Gamemodes")
    modpack = QuerySelectField("ModPacks")
    submit = SubmitField('Create Profile', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-black py-2 px-5 rounded-full font-bold text-md transition duration-300"})

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    submit = SubmitField('Login', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    submit = SubmitField('Login', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})

class AddProfileRotationForm(FlaskForm):
    profileid = StringField('Profile ID', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    submit = SubmitField('Sumbit', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})

class NewModForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    id = StringField('Id', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    submit = SubmitField('Add', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})

class NewMapForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    id = StringField('Id', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    submit = SubmitField('Add', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})

class NewGamemodeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    id = StringField('Id', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    submit = SubmitField('Add', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})

class NewModpackForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    id = StringField('Id', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    submit = SubmitField('Add', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})
