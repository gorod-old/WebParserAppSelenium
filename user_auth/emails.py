from django.core.mail import EmailMessage
from django.template.loader import get_template
from webparserapp.settings import setup


def send_account_verification_link(data):
    mail_subject = 'Activate your account.'
    context = {
        'user': data['user'],
        'domain': data['domain'],
        'uid': data['uid'],
        'token': data['token'],
    }
    print('msg context: ', context)
    message = get_template('user_auth/verification_email.html').render(context)
    print('email msg: ', message)
    print('from email:', setup.EMAIL_HOST_USER)
    recipient_list = [data['email']]
    msg = EmailMessage(
        mail_subject,
        message,
        setup.EMAIL_HOST_USER,
        recipient_list,
    )
    msg.content_subtype = "html"
    msg.send()
