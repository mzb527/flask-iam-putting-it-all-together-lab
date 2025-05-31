#!/usr/bin/env python3

from random import randint, choice as rc
from faker import Faker

from app import app
from models import db, Recipe, User
from config import bcrypt  # Ensure bcrypt is imported

fake = Faker()

with app.app_context():
    print("Deleting all records...")
    Recipe.query.delete()
    User.query.delete()

    print("Creating users...")

    users = []
    usernames = set()

    for _ in range(20):
        username = fake.unique.first_name()  # Ensure unique usernames
        usernames.add(username)

        user = User(
            username=username,
            bio=fake.paragraph(nb_sentences=3),
            image_url=fake.image_url(),
        )

        user.password_hash = bcrypt.generate_password_hash("securepassword").decode('utf-8')  # Secure hashing

        users.append(user)

    db.session.add_all(users)
    db.session.commit()  # Ensure users are saved before assigning recipes

    print("Creating recipes...")
    recipes = []
    for _ in range(100):
        instructions = fake.paragraph(nb_sentences=8)

        recipe = Recipe(
            title=fake.sentence(),
            instructions=instructions,
            minutes_to_complete=randint(15, 90),
            user=rc(users)  # Assign existing user
        )

        recipes.append(recipe)

    db.session.add_all(recipes)
    db.session.commit()
    print("Seeding complete.")