from flask import render_template, url_for, redirect, request
from flask_login import login_required, current_user
from datetime import datetime
from app.main import main
from app.main.forms import TryAppForm
from app.main.methods import send_confirmation_email
from app.dbModels import Owner


@main.route('/', methods=['GET', 'POST'])
def index():
    form = TryAppForm()
    if request.method == 'POST':
        # query number of pubs
        pubs = Owner.query.filter_by(city=form.city.data).count()
        return render_template('landing.html', city=form.city.data, pubs=pubs)
    elif current_user.is_authenticated and current_user.confirmed:
        return render_template('home.html')
    else:
        return render_template('landing.html', form=form, time=datetime.utcnow())


@main.route('/pricing')
def show_pricing():
    return render_template('pricing.html', title='Pricing')


@main.route('/contacts')
def contact():
    return render_template('contact_us.html', title='Let Us Know!', heading='We are glad to hear from you.')


@main.route('/find-a-pub')
def find_pub():
    return render_template('find_pub.html')


@main.route('/<callerPage>/work-in-progress')
def show_wip(callerPage):
    return render_template('errors/wip.html')


@main.route('/<callerRoute>/acc-confirmation')
@login_required
def send_confirmation(callerRoute):
    send_confirmation_email(recipient=current_user)
    if callerRoute == 'profile':
        return redirect(url_for('users.openProfile', userInfo=current_user.username))
