from .config import Settings
from .db import Database
from .repository import Repository


def settings() -> Settings:
    return Settings.from_env()


def repository() -> Repository:
    return Repository(Database(settings()))
