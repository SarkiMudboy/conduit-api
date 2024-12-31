from django.conf import settings
from django.db import connections

db_config = settings.DATABASES["default"]


def setup_db_connection(alias: str) -> str:
    if alias:
        connections.databases[alias] = db_config
    else:
        return "default"
    return alias


def delete_connection(alias: str) -> None:
    if alias in connections.databases:
        del connections.databases[alias]
