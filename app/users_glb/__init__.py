from flask import Blueprint

users = Blueprint('users', __name__)

from app.users_glb import routes
