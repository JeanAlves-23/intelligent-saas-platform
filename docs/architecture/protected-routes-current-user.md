# Protected Routes and Current User

Protected routes require a valid JWT access token sent through the HTTP `Authorization` header.

The current authenticated user is resolved from the token subject and loaded from the database.

## Authorization Header

Protected requests use:

```text
Authorization: Bearer <access_token>
```

The application extracts the Bearer token using FastAPI's HTTP Bearer authentication support.

## Authentication Flow

The protected request flow is:

```text
HTTP Request
    |
    v
Authorization: Bearer <JWT>
    |
    v
HTTPBearer
    |
    v
JWT Decode
    |
    +-- Validate signature
    +-- Validate expiration
    +-- Extract subject
    |
    v
User ID
    |
    v
Database Lookup
    |
    +-- User exists?
    +-- User active?
    |
    v
Authenticated User
    |
    v
Protected Endpoint
```

## Current User Dependency

Authenticated-user resolution is centralized in:

```text
app/api/dependencies/auth.py
```

The reusable dependency:

```text
get_current_user()
```

is responsible for:

- Reading the Bearer token.
- Decoding the JWT.
- Validating the token signature.
- Validating token expiration.
- Extracting the `sub` claim.
- Converting the subject into a user identifier.
- Loading the user from the database.
- Rejecting unknown users.
- Rejecting inactive users.

## Protected Endpoint

The current protected endpoint is:

```text
GET /auth/me
```

A valid authenticated request returns:

```text
200 OK
```

with the safe user representation.

Example:

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "email": "user@example.com",
  "full_name": "Example User",
  "is_active": true,
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z"
}
```

Sensitive fields are not exposed.

The response does not contain:

```text
password
password_hash
```

## Authentication Failures

Missing, invalid, malformed, or expired credentials return:

```text
401 Unauthorized
```

Invalid JWT credentials return:

```json
{
  "detail": "Could not validate credentials"
}
```

Inactive users return:

```text
403 Forbidden
```

with:

```json
{
  "detail": "Inactive user"
}
```

## Token Validation

JWT validation verifies:

- Signature integrity.
- Configured signing algorithm.
- Token expiration.
- Presence of the subject claim.
- Valid user identifier format.

A valid token is not sufficient by itself.

The application also verifies that the referenced user still exists and remains active.

## Testing

Protected-route tests cover:

- Valid access token.
- Missing token.
- Invalid token.
- Expired token.
- Inactive user.
- Current-user resolution.
- Safe API serialization.

## Current Scope

The protected-route foundation does not yet include:

- Refresh tokens
- Token revocation
- Logout
- Role-based authorization
- Organization-scoped authorization
- Permission enforcement
- MFA

These capabilities will be introduced in later iterations.