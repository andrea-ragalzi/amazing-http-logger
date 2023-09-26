"""
Module for defining entity functions for log data.

This module provides functions for converting log data between different
representations.

Functions:
    - logEntity(log): Function to convert a log document to a dictionary.
    - logResponseEntity(log): Function to convert a log document to a
      dictionary for a response.
    - logListEntity(logs): Function to convert a list of log documents to a
      list of dictionaries.

"""


def logEntity(log) -> dict:
    return {
        "id": str(log["_id"]),
        "created_at": log["created_at"],
        "updated_at": log["updated_at"],
        "request_type": log["request_type"],
        "url": log["url"],
        "client_ip": log["client_ip"],
        "status_code": log["status_code"],
        "user": log["user"]
    }


def logResponseEntity(log) -> dict:
    return {
        "id": str(log["_id"]),
        "created_at": log["created_at"],
        "updated_at": log["updated_at"],
        "request_type": log["request_type"],
        "url": log["url"],
        "client_ip": log["client_ip"],
        "status_code": log["status_code"],
        "user": log["user"]
    }


def logListEntity(logs) -> list:
    return [logEntity(log) for log in logs]
