import os
from typing import Any, Dict, Tuple

from django.http.request import HttpRequest
from django.template.loader import render_to_string

from ...tasks import send_ses_email, send_smtp_email
from .types import EmailData

CHARSET = "UTF-8"


class BaseEmailHandler:
    environment = os.getenv("DJANGO_SETTINGS_MODULE", "conduit.settings")
    env = environment.split(".")[1]


class EmailHandlerFactory(object):
    @staticmethod
    def build_handler(email_data: EmailData):
        handler = None
        base_class = BaseEmailHandler()

        match base_class.env:
            case "develop" | "testing" | "settings":
                handler = SMTPHandler()
            case "prod":
                handler = SESEmailHandler()
            case _:
                return

        handler.send_email(email_data)


class SESEmailHandler(BaseEmailHandler):

    REQUEST = HttpRequest()
    file: Tuple[str] = None

    def send_mail(self, email_data: EmailData) -> Dict[str, Any]:

        email_args = dict(
            Destination={
                "ToAddresses": email_data["to_email"],
                "CcAddresses": [],
                "BccAddresses": [],
            },
            ReplyToAddresses=[],
            Source=email_data["from_email"],
        )

        email_args["Message"] = self.build_html_mail(email_data)

        send_ses_email.delay(email_args)

    def build_html_mail(self, email_data: EmailData) -> Dict[str, Any]:

        return {
            "Body": {
                "Html": {
                    "Charset": CHARSET,
                    "Data": render_to_string(
                        email_data["template"], email_data["context"], self.REQUEST
                    ),
                },
                "Text": {
                    "Charset": CHARSET,
                    "Data": render_to_string(
                        email_data["template"], email_data["context"], self.REQUEST
                    ),
                },
            },
            "Subject": {"Charset": CHARSET, "Data": email_data["subject"]},
        }


class SMTPHandler(BaseEmailHandler):

    REQUEST = HttpRequest()

    def send_email(self, email_data: EmailData) -> None:

        email_args = [
            email_data.get("subject"),
            render_to_string(
                email_data["template"], email_data["context"], self.REQUEST
            ),
            email_data.get("from_email"),
            email_data.get("to_email"),
            [],
        ]

        send_smtp_email.delay(email_args)
