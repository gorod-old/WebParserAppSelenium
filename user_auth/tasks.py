from celery import shared_task
from user_auth.emails import send_account_verification_link


@shared_task
def send_acc_verification_mail(data):
    send_account_verification_link(data)
