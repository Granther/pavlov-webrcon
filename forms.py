from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, widgets
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms_sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from models import Mod

class QuerySelectMultipleFieldWithChecks(QuerySelectMultipleField):
    # Prefix false cause prefix to be on the right
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class SelectProfileForm(FlaskForm):
    profiles = SelectField('Choose a Profile', choices=[], validators=[DataRequired()], render_kw={"class": "bg-gray-900 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})
    submit = SubmitField('Set Profile', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})

class ModPackForm(FlaskForm):
    name = StringField('Modpack Name', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    mods = QuerySelectMultipleFieldWithChecks("Mods")
    submit = SubmitField('Sumbit', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-black py-2 px-5 rounded-full font-bold text-md transition duration-300"})

class NewProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    map = QuerySelectField("Map", render_kw={"class": "bg-gray-900 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})
    gamemode = QuerySelectField("Gamemode", render_kw={"class": "bg-gray-900 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})
    modpack = QuerySelectField("ModPack", render_kw={"class": "bg-gray-900 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})
    submit = SubmitField('Sumbit', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-black py-2 px-5 rounded-full font-bold text-md transition duration-300"})

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
    id = StringField('ID', default="UGC", validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    submit = SubmitField('Add', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})

class NewMapForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    id = StringField('ID', default="UGC", validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    submit = SubmitField('Add', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})

class NewGamemodeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    id = StringField('ID', default="UGC", validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    submit = SubmitField('Add', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})

class NewModpackForm(FlaskForm):
    name = StringField('Modpack Name', validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-white px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    id = StringField('ID', default="UGC", validators=[DataRequired()], render_kw={"class": "border border-black rounded-lg text-black px-2 py-1 focus:outline-none w-full text-lg", "autocomplete":"off"})
    submit = SubmitField('Add', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})

class RotateButton(FlaskForm):
    submit = SubmitField('Rotate', render_kw={"class": "bg-sky-500 hover:bg-sky-700 text-white py-2 px-5 rounded-full font-bold text-md transition duration-300"})
