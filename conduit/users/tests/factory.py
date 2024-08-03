from django.contrib.auth.models import AbstractBaseUser
import factory
from pytest_factoryboy import register
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from faker import Factory as FakerFactory

User: AbstractBaseUser = get_user_model()
faker = FakerFactory.create()

class UserFactory(DjangoModelFactory):

    class Meta:
        model = User

    email = factory.LazyFunction(lambda: faker.email())
    password = factory.django.Password("its-a-secret")
    avatar = ""