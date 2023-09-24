"""
Module for password hashing and authentication.

This module provides functions for hashing passwords and verifying passwords
against hashed passwords.

Dependencies:
    - Depends from fastapi: Depends function for dependency injection.
    - CryptContext from passlib.context: CryptContext class for password
      hashing.
    - AuthJWT from app.oauth2: AuthJWT class for JWT token handling.

Attributes:
    - pwd_context (CryptContext): CryptContext instance for password hashing.

Functions:
    - hash_password(password: str): Function to hash a password.
    - verify_password(password: str, hashed_password: str): Function to verify
      a password against a hashed password.
    - get_current_user(authorize: AuthJWT = Depends()): Function to retrieve
      the current authenticated user.

"""

from fastapi import Depends
from passlib.context import CryptContext

from oauth2 import AuthJWT

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def get_current_user(authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
        user_id = authorize.get_jwt_subject()
        return user_id
    except Exception:  # pylint: disable=broad-except
        return None
