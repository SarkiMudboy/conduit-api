import logging
from typing import Any, Dict, List

from celery import shared_task
from django.core.mail import EmailMessage

from ..apis.aws.services import AWSClientFactory

client = AWSClientFactory.build_client("ses")
logger = logging.getLogger("abstract")


@shared_task(name="Send SES Emails")
def send_ses_email(email_data: Dict[str, Any]) -> None:

    try:
        response = client.send_email(**email_data)
        message_id = response["MessageId"]
        logger.info(
            "Sent mail %s from %s to %s.",
            message_id,
            email_data.get("Source"),
            email_data["Destination"]["ToAddresses"][0],
        )
    except Exception as e:
        logger.exception(f"Couldn't send mail: f'{str(e)}'")
        raise


@shared_task(name="Send SMTP Emails")
def send_smtp_email(email_data: List[Any]) -> None:
    try:
        email = EmailMessage(*email_data)
        email.content_subtype = "html"
        email.send()

        logger.info("Email sent successfully.")
    except Exception as e:
        logger.exception(f"Error sending email: {e}")
