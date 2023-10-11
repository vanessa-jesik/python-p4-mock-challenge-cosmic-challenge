#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
api = Api(app)
migrate = Migrate(app, db)


db.init_app(app)

class Scientists(Resource):
    def get(self):
        scientists = Scientist.query.all()
        scientists_dict = [scientist.to_dict(rules=("-missions", "-planets")) for scientist in scientists]
        return make_response(jsonify(scientists_dict), 200)
    
    def post(self):
        scientist = Scientist()
        content = request.get_json()
        try:
            for key in content:
                if hasattr(scientist, key):
                    setattr(scientist, key, content[key])
            db.session.add(scientist)
            db.session.commit()
            response = make_response(jsonify(scientist.to_dict(rules=("-missions", "-planets"))), 201)
            response.headers = {"Content-Type": "application/json"}
            return response
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
    
class ScientistById(Resource):
    
    def get(self, id):
        scientist = Scientist.query.get(id)
        if scientist:
            scientist_dict = scientist.to_dict(rules=("-planets", "-missions.scientist", "-missions.planet.missions"))
            return make_response(jsonify(scientist_dict), 200)
        else:
            return make_response({"error": "Scientist not found"}, 400)
    
    def patch(self, id):
        scientist = Scientist.query.get(id)
        if scientist:
            try:
                content = request.get_json()
                for key in content:
                    if hasattr(scientist, key):
                        setattr(scientist, key, content[key])
                db.session.commit()
                return make_response(jsonify(scientist.to_dict(rules=("-missions", "-planets"))), 202)
            except ValueError:
                return make_response({"errors": ["validation errors"]}, 400)
        else:
            return make_response({"error": "Scientist not found"}, 404)
        
                
    
    def delete(self, id):
        scientist = Scientist.query.get(id)
        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            return make_response(jsonify(""), 204)
        else:
            return make_response({"error": "Scientist not found"},404)
    
api.add_resource(Scientists, "/scientists")
api.add_resource(ScientistById, "/scientists/<int:id>")

class Planets(Resource):
    def get(self):
        planets = Planet.query.all()
        planets_dict = [planet.to_dict(rules=("-missions", "-scientists")) for planet in planets]
        return make_response(jsonify(planets_dict), 200)
    
api.add_resource(Planets, "/planets")

class Missions(Resource):
    def post(self):
        mission = Mission()
        content = request.get_json()
        try:
            for key in content:
                if hasattr(mission, key):
                    setattr(mission, key, content[key])
            db.session.add(mission)
            db.session.commit()
            response = make_response(jsonify(mission.to_dict(rules=("-planet.missions", "-scientist.missions"))), 201)
            response.headers = {"Content-Type": "application/json"}
            return response
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
    
api.add_resource(Missions, "/missions")


if __name__ == '__main__':
    app.run(port=5555, debug=True)
