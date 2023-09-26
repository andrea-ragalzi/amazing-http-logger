"""
Module for handling authentication and authorization.

This module provides functions and classes for authentication and
authorization using JWT tokens.

Dependencies:
    - base64: Base64 module for decoding base64 encoded strings.
    - List from typing: List type hinting.
    - ObjectId from bson.objectid: ObjectId class for working with MongoDB
      document IDs.
    - Depends from fastapi: Depends function for dependency injection.
    - HTTPException from fastapi: HTTPException class for raising HTTP
      exceptions.
    - status from fastapi: status module for HTTP status codes.
    - AuthJWT from fastapi_jwt_auth: AuthJWT class for JWT token handling.
    - BaseModel from pydantic: BaseModel class for defining data models.

Attributes:
    - Settings (BaseModel): Data model for JWT configuration settings.

Exceptions:
    - NotVerified: Exception raised when the user is not verified.
    - UserNotFound: Exception raised when the user is not found.

Functions:
    - get_config(): Function to load JWT configuration settings.
    - require_user(): Function to require authentication and authorization for
      a user.
    - get_current_user(): Function to retrieve the current authenticated user.

"""

import base64
from typing import List

from bson.objectid import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from config import settings
from database import User
from serializers.userSerializers import userEntity


class Settings(BaseModel):
    authjwt_algorithm: str = settings.JWT_ALGORITHM
    authjwt_decode_algorithms: List[str] = [settings.JWT_ALGORITHM]
    authjwt_token_location: set = {'cookies', 'headers'}
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_cookie_csrf_protect: bool = False
    authjwt_public_key: str = base64.b64decode(
        settings.JWT_PUBLIC_KEY).decode('utf-8')
    authjwt_private_key: str = base64.b64decode(
        settings.JWT_PRIVATE_KEY).decode('utf-8')


@AuthJWT.load_config  # type: ignore
def get_config():
    return Settings()


class NotVerified(Exception):
    pass


class UserNotFound(Exception):
    pass


def require_user(authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
        user_id = authorize.get_jwt_subject()
        user = userEntity(User.find_one({'_id': ObjectId(str(user_id))}))

        if not user:
            raise UserNotFound('User no longer exist')

        if not user["verified"]:
            raise NotVerified('You are not verified')

    except Exception as err:  # pylint: disable=broad-except
        error = err.__class__.__name__
        print(error)
        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not logged in') from err
        if error == 'UserNotFound':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User no longer exist') from err
        if error == 'NotVerified':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Please verify your account') from err
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token is invalid or has expired') from err
    return user_id


def get_current_user(authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
        user_id = authorize.get_jwt_subject()
        return user_id
    except Exception as err:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=401,
            detail="Access token is not valid. Please log in again.") from err
