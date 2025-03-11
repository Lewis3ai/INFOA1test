from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# Define Pokemon model
class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __init__(self, name, type, description=None):
        self.name = name
        self.type = type
        self.description = description

    def get_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description
        }

    def __repr__(self):
        return f'<Pokemon {self.id} - {self.name}>'


# Define UserPokemon model for the many-to-many relationship between users and Pokemon
class UserPokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('user_pokemon', lazy=True))
    pokemon = db.relationship('Pokemon', backref=db.backref('user_pokemon', lazy=True))

    def __init__(self, user_id, pokemon_id):
        self.user_id = user_id
        self.pokemon_id = pokemon_id

    def get_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "pokemon_id": self.pokemon_id
        }

    def __repr__(self):
        return f'<UserPokemon {self.id} - User {self.user_id} with Pokemon {self.pokemon_id}>'


# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(50))
    __mapper_args__ = {'polymorphic_identity': 'user', 'polymorphic_on': type}

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='scrypt')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.id} {self.username} - {self.email}>'

    def get_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "type": self.type
        }




