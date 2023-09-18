"""
Module for configuration settings.

This module defines a `Settings` class that inherits from `BaseSettings` in
the `pydantic` module. It contains configuration variables that are loaded
from environment variables or from an `.env` file.

Dependencies:
    - BaseSettings from pydantic: BaseSettings class for defining
      configuration settings.

Attributes:
    - DATABASE_URL (str): The URL of the database.
    - MONGO_INITDB_DATABASE (str): The name of the MongoDB database.
    - JWT_PUBLIC_KEY (str): The public key for JWT token validation.
    - JWT_PRIVATE_KEY (str): The private key for JWT token signing.
    - REFRESH_TOKEN_EXPIRES_IN (int): The expiration time for refresh tokens.
    - ACCESS_TOKEN_EXPIRES_IN (int): The expiration time for access tokens.
    - JWT_ALGORITHM (str): The algorithm used for JWT token signing and
      validation.
    - CLIENT_ORIGIN (str): The origin of the client.
    - MONGO_INITDB_ROOT_USERNAME (str): The username for the MongoDB root user.
    - MONGO_INITDB_ROOT_PASSWORD (str): The password for the MongoDB root user.

Classes:
    - Settings (BaseSettings): Class for defining configuration settings.

"""

# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    MONGO_INITDB_DATABASE: str

    JWT_PUBLIC_KEY: str
    JWT_PRIVATE_KEY: str
    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int
    JWT_ALGORITHM: str

    CLIENT_ORIGIN: str

    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str

    class Config:
        env_file = './.env'


settings = Settings()
