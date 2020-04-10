from flask import render_template
from flask_mail import Message
from teamgate import mail


def sendEmail(user, templatePath, mailTitle, token=None):
    msg = Message('TeamGate Account -- ' + mailTitle.upper(),
                  sender='teamgate.help@gmail.com',
                  recipients=[user.email])
    if token:
        msg.body = render_template(templatePath + '.txt', token=token, user=user)
    else:
        msg.body = render_template(templatePath + '.txt', user=user)
    # _external parameter allow to generate an absolute URL whose works outside app environment
    mail.send(msg)
