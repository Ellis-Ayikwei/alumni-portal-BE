# Alumni API Documentation

## Overview

This document provides a comprehensive guide for developers to integrate with and use the Flask-based Alumni Management System API. It includes details on setup, endpoints, authentication flow, and system features.

---

## Prerequisites

- Python 3.x
- Redis
- pip
- virtualenv

---

## Setup and Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Set Up Virtual Environment

```bash
pip install virtualenv
python3 -m venv alumni-venv
source alumni-venv/bin/activate  # On Windows, use `alumni-venv\Scripts\activate`
```

### 3. Install Dependencies

```bash
pip install --no-cache-dir -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root with the following configuration:

```
MAIL_USERNAME=<your-email>
MAIL_PASSWORD=<your-app-password>
SECRET_KEY=<your-secret-key>
REDIS_URL=redis://localhost:6379/0
```

### 5. Start Redis Server

```bash
redis-server
```

### 6. Run the Application

```bash
# Activate virtual environment
source alumni-venv/bin/activate  # Linux/macOS
alumni-venv\Scripts\activate  # Windows

# Start the application
python -m api.v1.app  # Use `python3` on Linux/macOS if needed
```

---

## Project Structure

```
project-root/
|— api/v1/
    |— app.py          # Main entry point
    |— src/
        |— views/       # API views
            |— auth_views.py  # Authentication routes
            |— app_views.py   # Application routes
|— requirements.txt  # Dependencies
|— .env             # Environment configuration
```

---

## API Endpoints

### System Status Endpoints

| Endpoint                | Method | Description                    |
| ----------------------- | ------ | ------------------------------ |
| `/alumni/api/v1/status` | GET    | Check API status               |
| `/alumni/api/v1/`       | GET    | Index route                    |
| `/alumni/api/v1/stats`  | GET    | Retrieve counts of all classes |

### Authentication Endpoints

| Endpoint                                             | Method | Description          |
| ---------------------------------------------------- | ------ | -------------------- |
| `/alumni/api/v1/auth/register`                       | POST   | Register a new user  |
| `/alumni/api/v1/auth/login`                          | POST   | User login           |
| `/alumni/api/v1/auth/refresh_token`                  | POST   | Refresh access token |
| `/alumni/api/v1/auth/logout`                         | POST   | User logout          |
| `/alumni/api/v1/auth/recover`                        | POST   | Recover password     |
| `/alumni/api/v1/auth/reset_password/<token>/<email>` | POST   | Reset password       |

### User Management Endpoints

| Endpoint                                                 | Method           | Description                      |
| -------------------------------------------------------- | ---------------- | -------------------------------- |
| `/alumni/api/v1/users`                                   | GET, POST        | Retrieve all users / Create user |
| `/alumni/api/v1/users/<user_id>`                         | GET, PUT, DELETE | Retrieve, update, or delete user |
| `/alumni/api/v1/users/reset_password/<user_id>`          | PUT              | Reset user's password            |
| `/alumni/api/v1/users/my_profile/<user_id>`              | GET              | Retrieve user profile            |
| `/alumni/api/v1/users/user_profile_completion/<user_id>` | GET              | Calculate profile completion     |

### Alumni Groups Endpoints

| Endpoint                                              | Method           | Description                       |
| ----------------------------------------------------- | ---------------- | --------------------------------- |
| `/alumni/api/v1/alumni_groups`                        | GET, POST        | Retrieve/create alumni groups     |
| `/alumni/api/v1/alumni_groups/<group_id>`             | GET, PUT, DELETE | Retrieve, update, or delete group |
| `/alumni/api/v1/alumni_groups/<group_id>/invite_code` | POST             | Generate invite code              |
| `/alumni/api/v1/alumni_groups/my_groups/<user_id>`    | GET              | Retrieve user’s groups            |

### Payments Endpoints

| Endpoint                                           | Method           | Description                            |
| -------------------------------------------------- | ---------------- | -------------------------------------- |
| `/alumni/api/v1/payments`                          | GET, POST        | Retrieve all payments / Create payment |
| `/alumni/api/v1/payments/<payment_id>`             | GET, PUT, DELETE | Retrieve, update, or delete payment    |
| `/alumni/api/v1/payments/users_payments/<user_id>` | GET              | Retrieve user’s payments               |

---

## Authentication Flow

The API implements a secure token-based authentication system using Flask-JWT-Extended.

### Token Types

1. **Access Token**: Short-lived, used for accessing secure endpoints.
2. **Refresh Token**: Long-lived, used for generating new access tokens.

### User Login Flow

1. User submits credentials to `/auth/login`.
2. API validates credentials and returns:
   - Access Token
   - Refresh Token

### Token Refresh

- Use `/auth/refresh_token` to obtain a new Access Token using a valid Refresh Token.

### Password Recovery

1. Submit email to `/auth/recover`.
2. System sends a password reset link containing a token.
3. Use the link to reset the password via `/auth/reset_password/<token>/<email>`.

### Security Features

- Token blacklisting for logout.
- Password hashing with strong algorithms.
- Account activation checks.

---

## System Features

- Comprehensive user and group management.
- Redis-based token management.
- Insurance packages and payments tracking.
- Secure file uploads and downloads.

---

## Database Schema

The system utilizes the following database tables:

- `alumni_groups`
- `amendments`
- `attachments`
- `audit_trails`
- `beneficiaries`
- `benefits`
- `claims`
- `contract_members`
- `contracts`
- `group_members`
- `insurance_packages`
- `invites`
- `invoices`
- `payment_methods`
- `payments`
- `users`

---

## Database Operations

The `DBStorage` class provides various utility functions for interacting with the database.

### Core Functions

#### 1. `all`

Fetches all objects of a given class or all classes.

```python
def all(self, cls=None):
    """Query the current database session for all objects or specific class."""
    ...
```

#### 2. `new`

Adds a new object to the session.

```python
def new(self, obj):
    """Add the object to the current database session."""
    ...
```

#### 3. `save`

Commits all changes to the database.

```python
def save(self):
    """Commit all changes of the current database session."""
    ...
```

#### 4. `delete`

Deletes an object from the session.

```python
def delete(self, obj=None):
    """Delete from the current database session obj if not None."""
    ...
```

#### 5. `reload`

Reloads data from the database and initializes a session.

```python
def reload(self):
    """Reloads data from the database."""
    ...
```

#### 6. `close`

Removes the current session.

```python
def close(self):
    """Call remove() method on the private session attribute."""
    ...
```

#### 7. `get`

Retrieves an object by class and ID.

```python
def get(self, cls, id):
    """Retrieve the object based on the class name and ID, or None if not found."""
    ...
```

#### 8. `count`

Counts the number of objects in storage.

```python
def count(self, cls=None):
    """Count the number of objects in storage."""
    ...
```

#### 9. `get_database_tables`

Retrieves the list of table names dynamically.

```python
def get_database_tables(self):
    """Retrieve the list of table names from the connected database."""
    ...
```

---

## BaseModel Functions

The `BaseModel` class provides foundational functionality for all models.

### Core Functions

#### 1. `save`

Updates the `updated_at` attribute and saves the instance.

```python
def save(self):
    """Updates the attribute 'updated_at' with the current datetime."""
    ...
```

#### 2. `delete`

Deletes the current instance from storage.

```python
def delete(self):
    """Delete the current instance from the storage."""
    ...
```

#### 3. `to_dict`

Converts the model instance into a dictionary.

```python
def to_dict(self, save_fs=None):
    """Returns a dictionary containing all keys/values of the instance."""
    ...
```

#### 4. `__str__`

Returns a string representation of the instance.

```python
def __str__(self):
    """Return a string representation of an instance."""
    ...
```

#### 5. `__init__`

Initializes the base model with dynamic attributes.

```python
def __init__(self, *args, **kwargs):
    """Initialization of the base model."""
    ...
```

---

## Examples and Use Cases

### Using `DBStorage` Functions

#### Fetch All Users

```python
from models import storage
users = storage.all("User")
for user_id, user in users.items():
    print(f"User ID: {user_id}, User Info: {user.to_dict()}")
```

#### Create a New Group

```python
from models.alumni_group import AlumniGroup
from models import storage

new_group = AlumniGroup(name="Class of 2024", description="Graduating class")
storage.new(new_group)
storage.save()
```

### Using `BaseModel`

#### Create and Save a User

```python
from models.user import User

user = User(first_name="John", last_name="Doe", email="john.doe@example.com")
user.save()
print(user.to_dict())
```

#### Delete a User

```python
user.delete()
```

---

## Error Handling

### Common Errors and Responses

| Error Code | Description                          | Response Example                     |
| ---------- | ------------------------------------ | ------------------------------------- |
| 400        | Bad Request                          | `{ "error": "Invalid input" }`      |
| 401        | Unauthorized                         | `{ "error": "Unauthorized access" }`|
| 404        | Not Found                            | `{ "error": "Resource not found" }` |
| 500        | Internal Server Error                | `{ "error": "An unexpected error" }`|

### Debugging Tips

- Ensure the `.env` file is correctly configured.
- Check Redis server status.
- Review logs for stack traces.



---

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-JWT-Extended Documentation](https://flask-jwt-extended.readthedocs.io/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/docs/)

