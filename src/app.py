from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import src.schema as schema
import os
from datetime import timedelta


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET']
jwt = JWTManager(app)


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if username == os.environ['WEB_USER'] and password == os.environ['WEB_PASSWORD']:
        access_token = create_access_token(identity=username,expires_delta = timedelta(hours=12))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid username or password"}), 401


@app.route('/movies',methods=['GET'])
def list_movies():
    try:
        movies_list = schema.movies_list()
        return jsonify(movies_list),200
    except:
        return jsonify({"msg":"Unexpected error occured"},500)

@app.route('/movies',methods=['POST'])
@jwt_required()
def add_or_update():
    data = request.json
    if ("actors_ids" in data.keys() or "genres_ids" in data.keys() or "technicians_ids" in data.keys() or "year" in data.keys() or "name" in data.keys() or "id" in data.keys()):
        return jsonify(result=schema.add_update(data)),200
    else:
        return jsonify({"msg":"invalid input"}),400

@app.route('/movies/filter',methods=['GET'])
def list_movie_filter():
    data = request.json
    if ("actors_ids" in data.keys() or "genres_ids" in data.keys() or "technicians_ids" in data.keys()):
        return jsonify(schema.movies_list(data)),200
    else:
        return jsonify({"msg":"invalid input"}),400

@app.route('/actors/delete/<int:id>',methods=['POST'])
@jwt_required()
def delete_actor(id):
    return jsonify(result=schema.delete_actor(id)),200
