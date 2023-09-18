"""
Module for defining entity functions for user data.

This module provides functions for converting user data between
different representations.

Functions:
    - userEntity(user): Function to convert a user document to a dictionary.
    - userResponseEntity(user): Function to convert a user document to a
      dictionary for a response.
    - embeddedUserResponse(user): Function to convert a user document to a
      dictionary for an embedded response.
    - userListEntity(users): Function to convert a list of user documents to a
      list of dictionaries.

"""


def userEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "photo": user["photo"],
        "verified": user["verified"],
        "password": user["password"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
    }


def userResponseEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "photo": user["photo"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
    }


def embeddedUserResponse(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "photo": user["photo"]
    }


def userListEntity(users) -> list:
    return [userEntity(user) for user in users]
