from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'glorp'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rcon.db'

db = SQLAlchemy(app)

class Maps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    map_id = db.Column(db.String, unique=True, nullable=False)
    display_name = db.Column(db.String, unique=True, nullable=False)

class Gamemodes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gamemode_id = db.Column(db.String, unique=True, nullable=False)
    display_name = db.Column(db.String, unique=True, nullable=False)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    # with app.app_context():
    #     map = Maps(map_id="10", display_name="Funny map")
    #     db.session.add(map)
    #     game = Gamemodes(gamemode_id="90", display_name="Silly")
    #     db.session.add(game)
    #     db.session.commit()

    resmaps = Maps.query.all()
    resgames = Gamemodes.query.all()

    maps = []
    gamemodes = []

    for map in resmaps:
        maps.append({"map_id": map.map_id, "display_name": map.display_name})

    for game in resgames:
        gamemodes.append({"gamemode_id": game.gamemode_id, "display_name": game.display_name})

    queue = requests.get("http://localhost:5002/get").json()

    print(maps, gamemodes)
    return render_template("index.html", maps=maps, gamemodes=gamemodes, queue=queue)

@app.route("/submit", methods=["POST"])
def submit():
    map = request.form.get('map')
    game = request.form.get('game')

    url = 'http://localhost:5002/add'

    params = {
        'map': map,
        'gamemode': game,
        'uuid': str(uuid.uuid4())
    }

    response = requests.post(url, json=params)

    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
