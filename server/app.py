#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe, UserSchema, RecipeSchema

user_schema = UserSchema()
recipe_schema = RecipeSchema()
recipe_list_schema = RecipeSchema(many=True)

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        image_url = data.get("image_url")
        bio = data.get("bio")

        if not username or not password:
            return {"error": "Username and password required"}, 400

        try:
            user = User(username=username, image_url=image_url, bio=bio)
            user.password_hash = password  # Hashing handled in setter method
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id  # Log user in
            return user_schema.dump(user), 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Username already taken"}, 409

class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {}, 204

        user = User.query.get(user_id)
        return user_schema.dump(user), 200

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()

        if not user or not user.authenticate(password):
            return {"error": "Invalid credentials"}, 401

        session["user_id"] = user.id
        return user_schema.dump(user), 200

class Logout(Resource):
    def delete(self):
        session["user_id"] = None
        return {}, 204

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        recipes = Recipe.query.all()
        return recipe_list_schema.dump(recipes), 200

    def post(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()
        title = data.get("title")
        instructions = data.get("instructions")
        minutes_to_complete = data.get("minutes_to_complete")

        if not title or not instructions or len(instructions) < 50:
            return {"error": "Invalid recipe data"}, 422

        user = User.query.get(user_id)
        recipe = Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=minutes_to_complete,
            user=user
        )

        db.session.add(recipe)
        db.session.commit()
        return recipe_schema.dump(recipe), 201

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)