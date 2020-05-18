#   runs the Flask application instance created by __init__.py

from app import create_app
from config import set_Config

if __name__ == '__main__':
    app = create_app(config=set_Config())
    app.run()
