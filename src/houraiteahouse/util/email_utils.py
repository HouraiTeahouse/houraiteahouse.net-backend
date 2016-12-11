from flask import current_app
from flask_mail import Message
from ..common import mail


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)


# Files will be /var/htwebsite/email/[language code]/template, subject will be same + '_subject'
def load_template(template_name, language='en'):
    f = open('/var/htwebsite/email/{0}/{1}'.format(language, template_name + '_subject'))
    subject = f.readline()[:-1]
    f.close()
    
    f = open('/var/htwebsite/email/{0}/{1}'.format(language, template_name))
    template = f.read()
    f.close()
    
    return subject, template
