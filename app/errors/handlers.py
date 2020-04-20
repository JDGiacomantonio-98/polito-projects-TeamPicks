from flask import render_template
from app.errors import errors


@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', title='error: 403 - you cannot do that!'), 403


@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', title='error: 404 - page not found'), 404


@errors.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', title='error: 500 - what happened?'), 500
