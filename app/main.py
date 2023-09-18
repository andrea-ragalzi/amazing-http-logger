"""
Main module for the Amazing Http Logger application.

This module initializes the FastAPI application, sets up CORS middleware,
and includes the routers for authentication, user-related operations,
and log-related operations.

Dependencies:
    - FastAPI from fastapi: FastAPI class for creating the application.
    - CORSMiddleware from fastapi.middleware.cors: CORSMiddleware class for
      handling Cross-Origin Resource Sharing.
    - settings from app.config: Module for accessing application settings.
    - auth from app.routers: Module for authentication-related routes.
    - user from app.routers: Module for user-related routes.
    - log from app.routers: Module for log-related routes.

Routes:
    - GET '/api/healthchecker': Endpoint for checking the health of the
      application.

"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, user, log

app = FastAPI()

origins = [
    settings.CLIENT_ORIGIN,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, tags=['Auth'], prefix='/api/auth')
app.include_router(user.router, tags=['Users'], prefix='/api/users')
app.include_router(log.router, tags=['Logs'], prefix="/api/logs")


@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI with MongoDB"}
