import click
import csv
from tabulate import tabulate
from App import db, User, Pokemon, UserPokemon
from App import app, initialize_db
from sqlalchemy.exc import IntegrityError

@app.cli.command("init", help="Creates and initializes the database")
def initialize():
  initialize_db()
  print("Database Initialized!")




@app.cli.command("get-user", help="Retrieves a User by username or id")
@click.argument('key', default='bob')
def get_user(key):
    user = User.query.filter_by(username=key).first()
    if not user:
        user = User.query.get(int(key))
        if not user:
            print(f'{key} not found!')
            return
    print(user)

@app.cli.command("change-email")
@click.argument('username')
@click.argument('email')
def change_email(username, email):
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f'{username} not found!')
        return
    user.email = email
    db.session.commit()
    print(user)

@app.cli.command('get-users')
def get_users():
    users = User.query.all()
    print(users)

@app.cli.command('create-user')
@click.argument('username')
@click.argument('email')
@click.argument('password')
def create_user(username, email, password):
    new_user = User(username, email, password)
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        print("Username or email already taken!")
    else:
        print(new_user)

@app.cli.command('delete-user')
@click.argument('username')
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f'{username} not found!')
        return
    db.session.delete(user)
    db.session.commit()
    print(f'{username} deleted')

@app.cli.command('add-pokemon')
@click.argument('username')
@click.argument('pokemon_id', type=int)
def add_pokemon(username, pokemon_id):
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f'{username} not found!')
        return
    pokemon = Pokemon.query.get(pokemon_id)
    if not pokemon:
        print(f'Pokemon ID {pokemon_id} not found!')
        return

    user_pokemon = UserPokemon(user_id=user.id, pokemon_id=pokemon.id, name=pokemon.name)
    db.session.add(user_pokemon)
    db.session.commit()
    print(f'Pokemon {pokemon.name} added to {username}!')

@app.cli.command('get-user-pokemon')
@click.argument('username')
def get_user_pokemon(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f'{username} not found!')
        return
    user_pokemon = UserPokemon.query.filter_by(user_id=user.id).all()
    print([f'Pokemon ID {up.pokemon_id}' for up in user_pokemon])

@app.cli.command('remove-pokemon')
@click.argument('username')
@click.argument('pokemon_id', type=int)
def remove_pokemon(username, pokemon_id):
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f'{username} not found!')
        return
    user_pokemon = UserPokemon.query.filter_by(user_id=user.id, pokemon_id=pokemon_id).first()
    if not user_pokemon:
        print(f'Pokemon ID {pokemon_id} not found for {username}!')
        return
    db.session.delete(user_pokemon)
    db.session.commit()
    print(f'Pokemon ID {pokemon_id} removed from {username}!')

@app.cli.command('list-pokemon')
def list_pokemon():
    pokemon_list = Pokemon.query.all()
    data = [[p.id, p.name, p.type, p.description] for p in pokemon_list]
    print(tabulate(data, headers=["ID", "Name", "Type", "Description"]))