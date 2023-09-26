"""
Module for defining Pydantic schemas for user and log data.

This module provides Pydantic models for user-related data such as user
creation, login, and responses, as well as log-related data and responses.

Dependencies:
    - datetime from datetime: datetime module for working with dates and times.
    - BaseModel from pydantic: BaseModel class for defining data models.
    - EmailStr from pydantic: EmailStr class for validating email addresses.
    - constr from pydantic: constr class for validating string constraints.

Models:
    - UserBaseSchema (BaseModel): Base schema for user data.
    - CreateUserSchema (UserBaseSchema): Schema for creating a new user.
    - LoginUserSchema (BaseModel): Schema for user login.
    - UserResponseSchema (UserBaseSchema): Schema for user response.
    - UserResponse (BaseModel): Response schema for user data.
    - LogSchema (BaseModel): Schema for log data.
    - LogResponseSchema (LogSchema): Schema for log response.
    - LogResponse (BaseModel): Response schema for log data.
    - LogsResponse (BaseModel): Response schema for list of logs.

"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, constr


class UserBaseSchema(BaseModel):
    name: str
    email: EmailStr
    photo: str
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CreateUserSchema(UserBaseSchema):
    password: constr(min_length=8)  # type: ignore
    passwordConfirm: str
    verified: bool = False


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)  # type: ignore


class UserResponseSchema(UserBaseSchema):
    id: str


class UserResponse(BaseModel):
    status: str
    user: UserResponseSchema


class LogSchema(BaseModel):
    request_type: str
    url: str
    client_ip: str | None
    status_code: int
    created_at: datetime
    updated_at: datetime
    user: UserResponseSchema | None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class LogResponseSchema(LogSchema):
    id: str


class LogResponse(BaseModel):
    status: str
    log: LogSchema


class LogsResponse(BaseModel):
    status: str
    logs: list[LogSchema]
    
class CreateLogSchema(BaseModel):
    request_type: str
    url: str
    status_code: int
    
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
