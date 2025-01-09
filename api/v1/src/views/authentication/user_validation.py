#!/usr/bin/python3
"""Validates user data before saving it to the database"""
from cerberus import Validator


schema = {
    "email": {"type": "string", "regex": r"[^@]+@[^@]+\.[^@]+"},
    "first_name": {"type": "string", "regex": r"^[a-zA-Z]+$"},
    "last_name": {"type": "string", "regex": r"^[a-zA-Z]+$"},
    "phone_number": {"type": "string", "regex": r"^\d{10}$"},
    "address": {"type": "string", "minlength": 5, "empty": True},
    "city": {"type": "string"},
    "state": {"type": "string"},
    "zip_code": {"type": "string", "regex": r"^\d{5}(?:[-\s]\d{4})?$"},
    "country": {"type": "string"},
    "username": {"type": "string", "minlength": 4, "maxlength": 20},
    # 'role': {'type': 'string', 'allowed': ["regular", "admin", "superadmin"]},
    "password": {"type": "string", "minlength": 8},
    "other_names": {"type": "string", "empty": True},
}


def validate_user_data(user_data: dict) -> dict:
    """
    Validates user data against the predefined schema.

    Args:
        user_data (dict): The user data to be validated

    Returns:
        dict: The validated user data

    Raises:
        ValueError: If the data does not validate against the schema
    """
    validator = Validator(schema)
    validator.allow_unknown = True

    # Remove leading and trailing whitespace from string values
    for key, value in user_data.items():
        if isinstance(value, str) and value.strip() != '':
            user_data[key] = value.strip()

    if validator.validate(user_data):
        return user_data

    # Raise a ValueError with the validation errors
    validation_errors = ', '.join(
        f'{key}: {error}' for key, error in validator.errors.items()
    )
    raise ValueError(validation_errors)
