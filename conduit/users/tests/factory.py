import secrets

import factory
import pendulum
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from factory.django import DjangoModelFactory
from faker import Factory as FakerFactory

from ..models import OTP

User: AbstractBaseUser = get_user_model()
faker = FakerFactory.create()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.LazyFunction(lambda: faker.email())
    password = factory.django.Password("its-a-secret")
    avatar = ""


class OTPFactory(DjangoModelFactory):
    class Meta:
        model = OTP

    owner = factory.SubFactory(UserFactory)
    otp = factory.LazyAttribute(
        lambda _: "".join(f"{secrets.randbelow(10)}" for _ in range(6))
    )
    expiry = pendulum.now("UTC").add(minutes=10)
    claimed = False
