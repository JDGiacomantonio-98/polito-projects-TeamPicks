"""runs the Flask application instance created by __init__.py"""

from teamgate import app

if __name__ == '__main__':
    app.run(debug=True)
