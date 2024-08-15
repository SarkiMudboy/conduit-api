import random

import factory
import factory.fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from ..models import Drive, Object

fake = Faker()


class DriveFactory(DjangoModelFactory):
    class Meta:
        model = Drive

    type = "shared"
    # type = factory.fuzzy.FuzzyChoice(DriveType.choices, getter= lambda d: d[1])
    size = factory.LazyAttribute(lambda _: random.randint(20000, 4000000))
    # used = factory.LazyAttribute(lambda _: (factory.SelfAttribute('size')/2))

    @factory.post_generation
    def members(self, create, extracted: list, **kwargs):
        if not create or not extracted:
            return
        self.members.add(*extracted)


class ObjectFactory(DjangoModelFactory):
    class Meta:
        model = Object

    name = factory.LazyAttribute(lambda _: fake.file_name(extension="txt"))
    is_directory = factory.fuzzy.FuzzyChoice([True, False])
    drive = factory.SubFactory(DriveFactory)
    path = "/user/"
    metadata = {"Author": "Abdul"}
    size = size = factory.LazyAttribute(lambda _: random.randint(2000, 40000))
