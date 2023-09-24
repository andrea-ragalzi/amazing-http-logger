"""
Module for handling log-related operations.

This module provides API endpoints for creating and retrieving logs.

Dependencies:
    - Optional from typing: Optional type hinting.
    - datetime from datetime: Datetime module for working with dates and times.
    - ObjectId from bson: ObjectId class for working with MongoDB document IDs.
    - APIRouter from fastapi: APIRouter class for defining API endpoints.
    - Depends from fastapi: Depends function for dependency injection.
    - HTTPException from fastapi: HTTPException class for raising HTTP
      exceptions.
    - status from fastapi: status module for HTTP status codes.
    - schemas from app: Module for defining data schemas.
    - Log from app.database: Log class for interacting with the log
      collection in the database.
    - User from app.database: User class for interacting with the user
      collection in the database.
    - LogSchema from app.schemas: LogSchema class for validating log data.
    - logResponseEntity from app.serializers.logSerializers: logResponseEntity
      class for serializing log data.
    - get_current_user from app.utils: get_current_user function for
      retrieving the current user.

Routes:
    - POST '/': Endpoint for creating a log.
    - GET '/': Endpoint for retrieving logs.

"""

from typing import Optional
from datetime import datetime
from bson import ObjectId

from fastapi import APIRouter, Depends, HTTPException, status

import schemas
from database import Log, User
from schemas import LogSchema
from serializers.logSerializers import logResponseEntity
from utils import get_current_user

router = APIRouter()


@router.post('', response_model=schemas.LogResponse,
             status_code=status.HTTP_201_CREATED)
async def create_log(payload: LogSchema,
                     current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized")
    payload.created_at = datetime.utcnow()
    payload.userID = current_user
    result = Log.insert_one(payload.dict())
    new_log = logResponseEntity(Log.find_one({'_id': result.inserted_id}))
    return {"status": "success", "log": new_log}


@router.get('', response_model=schemas.LogsResponse,
            status_code=status.HTTP_200_OK)
async def get_logs(
    userID: Optional[str] = None,
    order_by: Optional[str] = "created_at",
    ascending: Optional[bool] = False,
    current_user: User = Depends(get_current_user)
):
    sort_option = [(order_by, 1 if ascending else -1)]

    filter_query = {}

    if userID:
        filter_query["userID"] = ObjectId(userID)

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not logged in"
        )

    logs = list(Log.find(filter_query).sort(sort_option))

    for log in logs:
        log['userID'] = str(log['userID'])

    return {"status": "success", "logs": logs}
