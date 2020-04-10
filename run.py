# runs the Flask application instance created by __init__.py

from app import create_app

# here a menu can be added in order to create different instances of app working with different Configs

app = create_app()

if __name__ == '__main__':
    app.run()
