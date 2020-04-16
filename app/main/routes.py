from flask import render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user
from app.main.forms import trialForm, resetRequestForm
from app.main.methods import sendEmail
from app.dbModel import User, Pub
from app.main import main
from datetime import datetime


@main.route('/', methods=['GET', 'POST'])
def index():
    form = trialForm()
    if request.method == 'POST':
        # query number of pubs
        pubs = Pub.query.filter_by(city=form.city.data).count()
        return render_template('landingPage.html', city=form.city.data, pubs=pubs)
    elif current_user.is_authenticated and current_user.confirmed:
        return render_template('homePage.html')
    else:
        return render_template('landingPage.html', form=form, time=datetime.utcnow())


@main.route('/pricing')
def showPricing():
    return render_template('pricing.html', title='Pricing')


@main.route('/contacts')
def contact():
    return render_template('contactUs.html', title='Let Us Know!', heading='We are glad to hear from you.')


@main.route('/find-a-pub')
def findPub():
    return render_template('findPub.html')


@main.route('/<callerPage>/work-in-progress')
def show_wip(callerPage):
    return render_template('errors/wip.html')


@main.route('/confirm-account/<token>')
def confirmAccount(token):
    # if user comes from email confirmation link there is no current user to check
    if current_user.confirmed:
        flash('You account has already been activated.', 'secondary')
        return redirect(url_for('main.index'))
    if current_user.confirmAccount(token):
        flash('Account confirmed successfully. Great, you are good to go now!', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'danger')
    return redirect(url_for('main.index'))


@main.route('/reset-request', methods=['GET', 'POST'])
def send_resetRequest():
    if current_user.is_authenticated and current_user.confirmed:
        flash('You are logged in already.', 'info')
        return redirect(url_for('main.index'))
    form = resetRequestForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # send user an email
            query = User.query.filter_by(email=form.emailAddr.data).first()
            if not query:
                query = Pub.query.filter_by(email=form.emailAddr.data).first()
            if query.confirmed:
                sendEmail(query, 'email-copy/reset-psw', 'psw reset', token=query.createToken())
                flash('An email has been sent to your inbox containing all instructions to reset your password!', 'warning')
                return redirect(url_for('users.login'))
            else:
                flash("Your account still require activation. Please check your email inbox.", 'warning')
                return redirect(url_for('users.login'))
    return render_template('resetRequest.html', title='Reset your psw', form=form)


@main.route('/<callerRoute>/acc-confirmation')
@login_required
def sendConfirmation(callerRoute):
    current_user.send_ConfirmationEmail()
    if callerRoute == 'profile':
        return redirect(url_for('users.showProfile', userInfo=current_user.username))


@main.route('/HTMLHelp')
def openVocabulary():
    return render_template('html-vocabulary.html')