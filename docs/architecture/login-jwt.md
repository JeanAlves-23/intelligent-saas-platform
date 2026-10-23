# Login and JWT Authentication

The login flow authenticates users with email and password credentials and returns a signed JWT access token.

The endpoint is:

```text
POST /auth/login
```

## Request

The login request contains:

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

The email is normalized before user lookup.

## Authentication Flow

The login flow follows these steps:

```text
HTTP Request
    |
    v
LoginRequest
    |
    v
Authentication Service
    |
    +-- Normalize email
    |
    +-- Find user
    |
    +-- Verify password
    |
    +-- Check active status
    |
    v
JWT Access Token
    |
    v
AccessTokenResponse
```

## Credential Validation

The authentication service validates:

- User existence.
- Password correctness.
- User active status.

Invalid email or password results in:

```text
401 Unauthorized
```

with:

```json
{
  "detail": "Invalid email or password"
}
```

Inactive users receive:

```text
403 Forbidden
```

with:

```json
{
  "detail": "Inactive user"
}
```

## JWT Access Token

Successful authentication returns a signed JWT access token.

The token contains:

```text
sub
iat
exp
```

Where:

- `sub` identifies the authenticated user.
- `iat` represents the token issue time.
- `exp` represents the token expiration time.

The signing algorithm and token expiration are configured through application settings.

## Configuration

JWT configuration is loaded from environment variables:

```text
JWT_SECRET_KEY
JWT_ALGORITHM
JWT_ACCESS_TOKEN_EXPIRE_MINUTES
```

The signing secret must not be committed as a real production credential.

## Successful Response

A successful login returns:

```text
200 OK
```

Example response:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

Sensitive user information is not included in the token response.

## Testing

The login flow includes tests for:

- Successful authentication.
- Access token generation.
- Correct token subject.
- Token expiration.
- Incorrect password rejection.
- Unknown email rejection.
- Inactive user rejection.
- HTTP status codes.
- Token response format.

## Current Scope

The current authentication flow does not include:

- Refresh tokens
- Logout/token revocation
- Password reset
- Email verification
- MFA
- Protected resource authorization
- Role-based authorization enforcement

These capabilities will be implemented in later iterations.