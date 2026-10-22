# User Registration

The registration flow allows a new user to create an account through the authentication API.

The endpoint is:

```text
POST /auth/register
```

## Request

The registration request contains:

```json
{
  "email": "user@example.com",
  "full_name": "Example User",
  "password": "SecurePassword123!"
}
```

The request is validated through a Pydantic schema.

Validation includes:

- Valid email format.
- Required full name.
- Minimum and maximum full name length.
- Minimum and maximum password length.

## Registration Flow

The application processes registration through the following layers:

```text
HTTP Request
    |
    v
FastAPI Route
    |
    v
UserRegisterRequest
    |
    v
Authentication Service
    |
    +-- Normalize email
    |
    +-- Check duplicate email
    |
    +-- Hash password
    |
    +-- Create User
    |
    v
SQLAlchemy
    |
    v
PostgreSQL
```

## Password Handling

The plain-text password is never stored in the database.

The service passes the password through the centralized security layer:

```text
Plain-text password
        |
        v
hash_password()
        |
        v
Argon2 hash
        |
        v
User.password_hash
```

Only the resulting password hash is persisted.

## Duplicate Email Handling

Email addresses are unique.

The registration service checks whether the email already exists before creating the user.

The database also enforces uniqueness as the final protection against duplicate records.

When registration is attempted with an existing email, the API returns:

```text
409 Conflict
```

with:

```json
{
  "detail": "Email already registered"
}
```

## Successful Response

A successful registration returns:

```text
201 Created
```

The response contains only the safe user representation:

```text
id
email
full_name
is_active
created_at
updated_at
```

The following values are never exposed:

```text
password
password_hash
```

## Validation Errors

Invalid request payloads return:

```text
422 Unprocessable Entity
```

Examples include:

- Invalid email format.
- Password shorter than the configured minimum.
- Missing required fields.

## Testing

The registration flow includes tests for:

- Successful user registration.
- Password hashing before persistence.
- Safe response serialization.
- Duplicate email rejection.
- Invalid email validation.
- Short password validation.
- Email normalization.

## Current Scope

The current registration flow does not include:

- Login
- JWT access tokens
- Refresh tokens
- Email verification
- Password reset
- Automatic organization creation
- Membership creation
- Authorization enforcement

These capabilities will be introduced in later iterations.