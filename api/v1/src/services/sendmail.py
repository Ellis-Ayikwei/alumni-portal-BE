#!/usr/bin/python3
from flask_mail import Message
from flask import current_app
from api.v1.app import mail


def send_email(recipient: str, subject: str, body: str, attachments: list = []) -> bool:
    """Sends an email using Flask-Mail."""
    msg = Message(
        subject=subject,
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[recipient],
        body=body,
    )
    for attachment in attachments:
        msg.attach(
            attachment.filename, attachment.content_type, attachment.read(), "inline"
        )
    return mail.send(msg)
