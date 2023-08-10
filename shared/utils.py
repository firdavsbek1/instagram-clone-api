import re
from decouple import config
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
import threading
from twilio.rest import Client

phone_number_pattern = "^\\+?[1-9][0-9]{7,14}$"
email_pattern = r"^\S+@\S+\.\S+$"
username_pattern = '^[a-zA-Z0-9_.-]+$'
VIA_EMAIL, VIA_PHONE = ['via_email', 'via_phone']

ERROR_MESSAGE = {
    "success": False,
    "message": "Username or email entered incorrectly!Please, try again!"
}


def validate_phone_number(phone_number):
    return re.match(phone_number_pattern, phone_number)


def validate_email(email):
    return re.match(email_pattern, email)


def validate_username(username):
    return re.match(username_pattern, username)


def validate_phone_or_email(email_phone_number):
    if validate_phone_number(email_phone_number):
        return VIA_PHONE
    elif validate_email(email_phone_number):
        return VIA_EMAIL
    else:
        raise ValidationError(ERROR_MESSAGE)


class EmailThread(threading.Thread):
    def __init__(self, subject, content, recipient_list):
        self.subject = subject
        self.content = content
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        email_message = EmailMessage(self.subject, self.content, to=self.recipient_list)
        email_message.content_subtype = 'html'
        email_message.send()


def send_mail(email, code):
    subject = "Instagram Account Confirmation"
    content = render_to_string('users/account_confirmation.html', {"code": code})
    EmailThread(subject, content, [email]).start()


def send_phone_number_confirm(phone_number, code):
    client = Client(
        config('TWILIO_ACCOUNT_SID'),
        config('TWILIO_AUTH_TOKEN')
    )
    message = client.messages.create(
        body=f"You number was requested for account registration on Gnstagram! You code is: {code}",
        to=phone_number,
        from_="+12187182860"
    )
    print(message.sid)


def identify_user_login_type(user_input):
    if validate_email(user_input):
        return 'email'
    elif validate_phone_number(user_input):
        return 'phone_number'
    elif validate_username(user_input):
        'username'
    else:
        ERROR_MESSAGE.update(message="Entered value not matches to username, email or phone_number!")
        raise ValidationError(ERROR_MESSAGE)
