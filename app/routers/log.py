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

from datetime import datetime
from typing import Optional

import schemas
from bson import ObjectId
from database import Log, User
from fastapi import APIRouter, Depends, HTTPException, Request, status
from oauth2 import require_user
from schemas import CreateLogSchema, UserResponseSchema
from serializers.logSerializers import logResponseEntity
from utils import get_current_user

router = APIRouter()


@router.post('', response_model=schemas.LogResponse,
             status_code=status.HTTP_201_CREATED)
async def create_log(payload: CreateLogSchema,
                     request: Request,
                     user_id: str = Depends(require_user)):
    new_log = schemas.LogSchema(
        request_type=payload.request_type,
        url=payload.url,
        client_ip=None,
        status_code=payload.status_code,
        user=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    if request.client:
        new_log.client_ip = request.client.host
    db_user = User.find_one({'_id': ObjectId(user_id)})
    if not db_user:
        Log.insert_one(new_log.dict())
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized")
    new_log.user = UserResponseSchema(
        id=str(db_user["_id"]),
        name=db_user["name"],
        email=db_user["email"],
        photo=db_user["photo"],
        role=db_user["role"],
        created_at=db_user["created_at"],
        updated_at=db_user["updated_at"]
    )
    result = Log.insert_one(new_log.dict())
    response_log = logResponseEntity(Log.find_one({'_id': result.inserted_id}))
    return {"status": "success", "log": response_log}


@router.get('', response_model=schemas.LogsResponse,
            status_code=status.HTTP_200_OK)
async def get_logs(
    userID: Optional[str] = None,
    order_by: Optional[str] = "created_at",
    ascending: Optional[bool] = False,
    current_user=Depends(get_current_user)
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

    logs = list(Log.find(filter_query).sort(sort_option))  # type: ignore

    for log in logs:
        log['user'] = str(log['user'])

    return {"status": "success", "logs": logs}
