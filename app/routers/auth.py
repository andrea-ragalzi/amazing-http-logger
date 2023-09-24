"""
Module for defining authentication-related API routes.

This module defines the API routes for user authentication using the FastAPI
framework.

Dependencies:
    - datetime from datetime: datetime class for working with dates and times.
    - timedelta from datetime: timedelta class for representing durations.
    - ObjectId from bson.objectid: ObjectId class for working with MongoDB
      ObjectIDs.
    - APIRouter from fastapi: APIRouter class for defining API routes.
    - Response from fastapi: Response class for defining HTTP responses.
    - status from fastapi: status module for defining HTTP status codes.
    - Depends from fastapi: Depends class for defining dependencies.
    - HTTPException from fastapi: HTTPException class for raising HTTP
      exceptions.
    - Log from app.database: Log collection from the MongoDB database.
    - User from app.database: User collection from the MongoDB database.
    - userEntity from app.serializers.userSerializers: Function for converting
      a user document to a dictionary.
    - userResponseEntity from app.serializers.userSerializers: Function for
      converting a user document to a dictionary for a response.
    - schemas from app: Module for defining schemas.
    - utils from app: Module for defining utility functions.
    - AuthJWT from app.oauth2: AuthJWT class for managing JWT authentication.
    - settings from app.config: settings module for accessing application
      configuration.

Attributes:
    - router (APIRouter): APIRouter instance for defining
      authentication-related API routes.
    - ACCESS_TOKEN_EXPIRES_IN (int): The expiration time (in minutes) for an
      access token.
    - REFRESH_TOKEN_EXPIRES_IN (int): The expiration time (in minutes) for a
      refresh token.

API Routes:
    - POST /register: Route for creating a new user account.
    - POST /login: Route for user login.
    - GET /refresh: Route for refreshing an access token.
    - GET /logout: Route for user logout.

"""

from datetime import datetime, timedelta
from bson.objectid import ObjectId
from fastapi import APIRouter, Response, status, Depends, HTTPException

from database import Log, User
from serializers.userSerializers import userEntity, userResponseEntity
import schemas, utils
from oauth2 import AuthJWT
from config import settings


router = APIRouter()
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN


@router.post('/register', status_code=status.HTTP_201_CREATED,
             response_model=schemas.UserResponse)
async def create_user(payload: schemas.CreateUserSchema):
    new_log = schemas.LogSchema(
        request_type='POST',
        url='http://127.0.0.1:8000/api/auth/register',
        client_ip='127.0.0.1',
        userID='',
        status_code=status.HTTP_201_CREATED,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    # Check if user already exist
    user = User.find_one({'email': payload.email.lower()})
    if user:
        new_log.userID = user.get('_id')
        new_log.status_code = status.HTTP_409_CONFLICT
        Log.insert_one(new_log.dict())
        raise HTTPException(status_code=new_log.status_code,
                            detail='Account already exist')
    # Compare password and passwordConfirm
    if payload.password != payload.passwordConfirm:
        new_log.status_code = status.HTTP_400_BAD_REQUEST
        Log.insert_one(new_log.dict())
        raise HTTPException(
            status_code=new_log.status_code,
            detail='Passwords do not match')
    #  Hash the password
    payload.password = utils.hash_password(payload.password)
    del payload.passwordConfirm
    payload.role = 'user'
    payload.verified = True
    payload.email = payload.email.lower()
    payload.created_at = datetime.utcnow()
    payload.updated_at = payload.created_at
    result = User.insert_one(payload.dict())
    new_user = userResponseEntity(User.find_one({'_id': result.inserted_id}))
    new_log.userID = result.inserted_id
    Log.insert_one(new_log.dict())
    return {"status": "success", "user": new_user}


@router.post('/login')
def login(
    payload: schemas.LoginUserSchema,
    response: Response,
    authorize: AuthJWT = Depends()
) -> dict[str, str | str]:
    new_log = schemas.LogSchema(
        request_type='POST',
        url='http://127.0.0.1:8000/api/auth/login',
        client_ip='127.0.0.1',
        status_code=200,
        userID='',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    # Check if the user exist
    db_user = User.find_one({'email': payload.email.lower()})
    new_log.userID = db_user.get('_id')
    if not db_user:
        new_log.status_code = status.HTTP_400_BAD_REQUEST
        Log.insert_one(new_log.dict())
        raise HTTPException(status_code=new_log.status_code,
                            detail='Incorrect Email or Password')
    user = userEntity(db_user)
    # Check if the password is valid
    if not utils.verify_password(payload.password, user['password']):
        new_log.status_code = status.HTTP_400_BAD_REQUEST
        Log.insert_one(new_log.dict())
        raise HTTPException(status_code=new_log.status_code,
                            detail='Incorrect Email or Password')

    # Create access token
    access_token = authorize.create_access_token(
        subject=str(user["id"]),
        expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))

    # Create refresh token
    new_token = authorize.create_refresh_token(
        subject=str(user["id"]),
        expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN))

    # Store refresh and access tokens in cookie
    response.set_cookie(
        'access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie(
        'refresh_token', new_token,
        REFRESH_TOKEN_EXPIRES_IN * 60,
        REFRESH_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie(
        'logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')
    Log.insert_one(new_log.dict())
    # Send both access
    return {'status': 'success', 'access_token': access_token}


@router.get('/refresh')
def refresh_token(response: Response, authorize: AuthJWT = Depends()):
    new_log = schemas.LogSchema(
        request_type='GET',
        url='http://127.0.0.1:8000/api/auth/refresh',
        client_ip='127.0.0.1',
        status_code=200,
        userID='',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    try:
        authorize.jwt_refresh_token_required()
        user_id = authorize.get_jwt_subject()
        if not user_id:
            new_log.status_code = status.HTTP_401_UNAUTHORIZED
            Log.insert_one(new_log.dict())
            raise HTTPException(status_code=new_log.status_code,
                                detail='Could not refresh access token')
        db_user = User.find_one({'_id': ObjectId(str(user_id))})
        user = userEntity(db_user)
        new_log.userID = db_user.get('_id')
        if not user:
            new_log.status_code = status.HTTP_401_UNAUTHORIZED
            Log.insert_one(new_log.dict())
            raise HTTPException(
                status_code=new_log.status_code,
                detail='The user belonging to this token no logger exist')
        access_token = authorize.create_access_token(
            subject=str(user["id"]), expires_time=timedelta(
                minutes=ACCESS_TOKEN_EXPIRES_IN))
    except Exception as err:
        error = err.__class__.__name__
        if error == 'MissingTokenError':
            new_log.status_code = status.HTTP_400_BAD_REQUEST
            Log.insert_one(new_log.dict())
            raise HTTPException(
                status_code=new_log.status_code,
                detail='Please provide refresh token') from err
        new_log.status_code = status.HTTP_400_BAD_REQUEST,
        Log.insert_one(new_log.dict())
        raise HTTPException(
            status_code=new_log.status_code,
            detail=error) from err

    response.set_cookie(
        'access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie(
        'logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')
    Log.insert_one(new_log.dict())
    return {'access_token': access_token}


@router.get('/logout', status_code=status.HTTP_200_OK)
def logout(response: Response, authorize: AuthJWT = Depends()):
    new_log = schemas.LogSchema(
        request_type='GET',
        url='http://127.0.0.1:8000/api/auth/logout',
        client_ip='127.0.0.1',
        status_code=200,
        userID='',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    user_id = authorize.get_jwt_subject()
    if user_id:
        db_user = User.find_one({'_id': ObjectId(str(user_id))})
        if db_user:
            new_log.userId = db_user.get('_id')
    authorize.unset_jwt_cookies()
    response.set_cookie('logged_in', '', -1)
    Log.insert_one(new_log.dict())
    return {'status': 'success'}
