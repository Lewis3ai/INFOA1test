import os, csv
from flask import Flask, jsonify, request
from functools import wraps
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)

from .models import db, User, UserPokemon, Pokemon

# Configure Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MySecretKey'
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config['JWT_HEADER_NAME'] = "Cookie"


# Initialize App 
db.init_app(app)
app.app_context().push()
CORS(app)
jwt = JWTManager(app)

# Initializer Function
def initialize_db():
  db.drop_all()
  db.create_all()


# Decorator to ensure the user is logged in
def login_required(f):
  @wraps(f)
  @jwt_required()  # Ensure JWT authentication
  def decorated_function(*args, **kwargs):
    user = User.query.filter_by(username=get_jwt_identity()).first()
    if not user:
      return jsonify(error='Unauthorized access'), 401
    return f(*args, **kwargs)
  return decorated_function


# Login user function
def login_user(username, password):
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    token = create_access_token(identity=username)
    response = jsonify(access_token=token)
    set_access_cookies(response, token)
    return response
  return jsonify(error="Invalid username or password"), 401


# Root route
@app.route('/')
def index():
  return '<h1>Poke API v1.0</h1>'


# Login
@app.route('/login', methods=['POST'])
def user_login_view():
  data = request.json
  return login_user(data['username'], data['password'])


# Sign Up
@app.route('/signup', methods=['POST'])
def signup_user_view():
  data = request.json
  try:
    new_user = User(data['username'], data['email'], data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify(
        message=f'User {new_user.id} - {new_user.username} created!'), 201
  except IntegrityError:
    db.session.rollback()
    return jsonify(error='Username already exists'), 400


# Logout
@app.route('/logout', methods=['GET'])
def logout():
  response = jsonify(message='Logged out')
  unset_jwt_cookies(response)
  return response


# Save a Pokémon (POST /mypokemon)
@app.route('/mypokemon', methods=['POST'])
@login_required
def save_pokemon():
  data = request.json
  username = get_jwt_identity()
  user = User.query.filter_by(username=username).first()
  pokemon = Pokemon.query.filter_by(id=data['pokemon_id']).first()

  if not pokemon:
    return jsonify(error='Pokemon not found'), 404

  user_pokemon = UserPokemon(user_id=user.id, pokemon_id=pokemon.id, name=data['name'])
  db.session.add(user_pokemon)
  db.session.commit()

  return jsonify(message=f'{pokemon.name} saved!'), 201


# Get the user's Pokémon (GET /mypokemon)
@app.route('/mypokemon', methods=['GET'])
@login_required
def list_my_pokemon():
  username = get_jwt_identity()
  user = User.query.filter_by(username=username).first()

  user_pokemon = UserPokemon.query.filter_by(user_id=user.id).all()
  pokemon_list = [pokemon.to_dict() for pokemon in user_pokemon]

  return jsonify(pokemon_list), 200


# Get specific Pokémon by ID (GET /mypokemon/:id)
@app.route('/mypokemon/<int:id>', methods=['GET'])
@login_required
def get_pokemon_by_id(id):
  username = get_jwt_identity()
  user = User.query.filter_by(username=username).first()

  user_pokemon = UserPokemon.query.filter_by(id=id, user_id=user.id).first()
  if not user_pokemon:
    return jsonify(error="Pokemon not found or unauthorized"), 401

  return jsonify(user_pokemon.to_dict()), 200


# Update Pokémon (PUT /mypokemon)
@app.route('/mypokemon', methods=['PUT'])
@login_required
def update_pokemon():
  data = request.json
  username = get_jwt_identity()
  user = User.query.filter_by(username=username).first()

  user_pokemon = UserPokemon.query.filter_by(id=data['id'], user_id=user.id).first()
  if not user_pokemon:
    return jsonify(error="Bad ID or unauthorized"), 401

  user_pokemon.name = data['name']
  db.session.commit()

  return jsonify(message=f"Pokemon updated to '{data['name']}'!"), 200


# Delete Pokémon (DELETE /mypokemon)
@app.route('/mypokemon', methods=['DELETE'])
@login_required
def delete_pokemon():
  data = request.json
  username = get_jwt_identity()
  user = User.query.filter_by(username=username).first()

  user_pokemon = UserPokemon.query.filter_by(id=data['id'], user_id=user.id).first()
  if not user_pokemon:
    return jsonify(error="Bad ID or unauthorized"), 401

  db.session.delete(user_pokemon)
  db.session.commit()

  return jsonify(message="Pokemon released!"), 200


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=81)