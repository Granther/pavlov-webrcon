from flask import Flask, request, jsonify, Response
import os
from jinja2 import Template
from dotenv import load_dotenv
import subprocess
from uuid import uuid4
import requests
import json

game_ini_path = '/home/steam/pavlovserver/Pavlov/Saved/Config/LinuxServer/Game.ini'
game_ini_path = 'Game.ini'
template_path = 'game_template.conf'

class DudeServer:
    def __init__(self):
        pass

    def load_template(self, path):
        with open(path, 'r') as file:
            return Template(file.read())

    def create_game_ini(self, rotations: list):
        template = self.load_template(template_path)
        config_content = template.render(rotations=rotations)

        with open(game_ini_path, 'w') as file:
            file.write(config_content)

app = Flask(__name__)
server = DudeServer()

# rotations = [{'id':'1', 'gamemode': 'GUN'}, {'id':'1', 'gamemode': 'GUN'}]
rotations = []

@app.route('/add', methods=['POST'])
def add():
    data = request.json
    map = data.get('map')
    gamemode = data.get('gamemode')
    uuid = data.get('uuid')

    rotations.append({"id": map, "gamemode": gamemode, "uuid": uuid})
    server.create_game_ini(rotations)

    return jsonify({"status": True})

@app.route('/delete/<uuid>', methods=['POST', 'GET'])
def delete(uuid):
    for item in rotations:
        if item['uuid'] == uuid:
            rotations.remove(item)
            return jsonify({"status": True})
        
@app.route('/get', methods=['GET'])
def get():
    return Response(json.dumps(rotations),  mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
