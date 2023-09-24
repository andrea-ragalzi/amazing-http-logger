"""
Module for defining user-related API routes.

This module defines the API routes for user-related operations using the
FastAPI framework.

Dependencies:
    - APIRouter from fastapi: APIRouter class for defining API routes.
    - Depends from fastapi: Depends class for defining dependencies.
    - ObjectId from bson.objectid: ObjectId class for working with MongoDB
      ObjectIDs.
    - userResponseEntity from app.serializers.userSerializers: Function for
      converting a user document to a dictionary for a response.
    - User from app.database: User collection from the MongoDB database.
    - schemas from app: Module for defining schemas.
    - require_user from app.oauth2: Function for requiring a user to be
      authenticated.

Attributes:
    - router (APIRouter): APIRouter instance for defining user-related API
      routes.

API Routes:
    - GET /me: Route for getting information about the current user.

"""

from fastapi import APIRouter, Depends
from bson.objectid import ObjectId
from serializers.userSerializers import userResponseEntity

from database import User
import schemas
from oauth2 import require_user

router = APIRouter()


@router.get('/me', response_model=schemas.UserResponse)
def get_me(user_id: str = Depends(require_user)):
    user = userResponseEntity(User.find_one({'_id': ObjectId(str(user_id))}))
    return {"status": "success", "user": user}
