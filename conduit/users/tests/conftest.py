from pytest_factoryboy import register

from .factory import OTPFactory, UserFactory

register(UserFactory)
register(OTPFactory)
