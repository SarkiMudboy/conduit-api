from .handlers import EmailHandlerFactory
from .types import EmailData


class BaseEmailClient(object):
    @classmethod
    def send(cls, email_data: EmailData):

        return cls.HANDLER_FACTORY.build_handler(email_data)


class EmailClient(BaseEmailClient):
    """
    Client for sending emails
    """

    HANDLER_FACTORY = EmailHandlerFactory
