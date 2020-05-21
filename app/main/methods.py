from threading import Thread

from flask import render_template, current_app, flash
from flask_mail import Message

from app import mail


def send_on_thread(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(recipient, templatePath=None, mailTitle=None, token=None, background=True):
    msg = Message('TeamPicks Account -- ' + mailTitle.upper(),
                  sender='teampicks.help@gmail.com',
                  recipients=[recipient.email])
    if token:
        msg.body = render_template(templatePath + '.txt', token=token, user=recipient)
    else:
        msg.body = render_template(templatePath + '.txt', user=recipient)
    # _external parameter allow to generate an absolute URL whose works outside app environment
    if background:
        Thread(target=send_on_thread, args=(current_app._get_current_object(), msg)).start()
    else:
        mail.send(msg)


def send_confirmation_email(recipient, flash_msg=False, background=True):
    msg = Message('TeamPicks Account -- ACCOUNT CONFIRMATION',
                  sender='teampicks.help@gmail.com',
                  recipients=[recipient.email])
    msg.body = render_template('email-copy/confirm-registration.txt', token=recipient.create_token(), user=recipient)
    # _external parameter allow to generate an absolute URL whose works outside app environment
    if background:
        Thread(target=send_on_thread, args=(current_app._get_current_object(), msg)).start()
    else:
        mail.send(msg)
    if flash_msg:
        flash('A confirmation email has been sent to you. Open your inbox!', 'warning')


def send_pswReset_email(recipient, flash_msg=False, background=True):
    msg = Message('TeamPicks Account -- PASSWORD RESET',
                  sender='teampicks.help@gmail.com',
                  recipients=[recipient.email])
    msg.body = render_template('email-copy/reset-psw.txt', token=recipient.create_token(), user=recipient)
    if background:
        Thread(target=send_on_thread, args=(current_app._get_current_object(), msg)).start()
    else:
        mail.send(msg)
    if flash_msg:
        flash('A confirmation email has been sent to you. Open your inbox!', 'warning')

