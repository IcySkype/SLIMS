from django.core.mail import send_mail
from django.conf import settings

def send_registration_email(user, password):
    """
    Sends a registration email to the user with their login credentials.
    """
    subject = 'Your New Account for the Science Lab Inventory Management System'
    message = f"""
    Hello {user.first_name} {user.last_name},

    Congratulations! Your account has been successfully created for our web application SLIMS.
    Here are your login credentials:

    Email: {user.email}
    Username: {user.username}
    Password: {password}

    You can log in using these credentials at any time.

    Best regards,
    IMCC Science Laboratory
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
