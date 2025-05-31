from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields
from config import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String, nullable=True)
    bio = db.Column(db.String, nullable=True)

    # Establish relationship with Recipe model
    recipes = db.relationship("Recipe", back_populates="user", lazy=True)

    # Protect password_hash property
    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes cannot be accessed directly.")

    # Set password hash property using bcrypt
    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Authenticate method to verify password
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    def __repr__(self):
        return f'User {self.username}, ID: {self.id}'

class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Establish relationship with User model
    user = db.relationship("User", back_populates="recipes")

    @validates("instructions")
    def validate_instructions(self, key, value):
        if len(value) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return value

    def __repr__(self):
        return f'Recipe {self.title}, ID: {self.id}'

class UserSchema(Schema):
    id = fields.Int()
    username = fields.String()
    image_url = fields.String()
    bio = fields.String()

class RecipeSchema(Schema):
    id = fields.Int()
    title = fields.String()
    instructions = fields.String()
    minutes_to_complete = fields.Int()
    user = fields.Nested(UserSchema)  # Serialize user within recipe responses