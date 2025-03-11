from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.functions import user
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()





    

# Define UserPokemon model for the many-to-many relationship between users and Pokemon
class UserPokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    
    user = db.relationship('User', backref=db.backref('user_pokemon', lazy=True))
    pokemon = db.relationship('Pokemon', backref=db.backref('user_pokemon', lazy=True))

    def __init__(self, user_id, pokemon_id, name):
        self.user_id = user_id
        self.pokemon_id = pokemon_id
        self.name = name

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


# Define Pokemon model
class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    attack = db.Column(db.Integer, nullable=False)
    defense = db.Column(db.Integer, nullable=False)
    hp = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    sp_attack = db.Column(db.Integer, nullable=False)
    sp_defense = db.Column(db.Integer, nullable=False)
    speed = db.Column(db.Integer, nullable=False)
    type1 = db.Column(db.String(50), nullable=False)
    type2 = db.Column(db.String(50), nullable=True)  # Nullable for single-type Pokemon

    def __init__(self, id, name, attack, defense, hp, height, weight, sp_attack, sp_defense, speed, type1, type2=None):
        self.id = id
        self.name = name
        self.attack = attack
        self.defense = defense
        self.hp = hp
        self.height = height
        self.weight = weight
        self.sp_attack = sp_attack
        self.sp_defense = sp_defense
        self.speed = speed
        self.type1 = type1
        self.type2 = type2

    def get_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "attack": self.attack,
            "defense": self.defense,
            "hp": self.hp,
            "height": self.height,
            "weight": self.height,
            "sp_attack": self.sp_attack,
            "sp_defense": self.sp_defense,
            "speed": self.speed,
            "type1": self.type1,
            "type2": self.type2
        }

    def __repr__(self):
        return f'<Pokemon {self.id} - {self.name}>'
