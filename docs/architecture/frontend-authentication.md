# Frontend Authentication Flow

The frontend authentication layer connects the React application to the existing FastAPI authentication endpoints.

## Backend Endpoints

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

## Frontend Responsibilities

The frontend authentication layer is responsible for:

- Registering new users.
- Authenticating existing users.
- Persisting the JWT access token.
- Automatically attaching the token to authenticated API requests.
- Restoring authenticated sessions.
- Loading the current authenticated user.
- Protecting private routes.
- Logging users out.
- Handling authentication errors.

## Authentication State

Authentication state is managed through `AuthContext`.

The context exposes:

```text
user
isAuthenticated
isLoading
login()
logout()
```

## Login Flow

```text
Login Form
    |
    v
POST /auth/login
    |
    v
JWT Access Token
    |
    v
Store Token
    |
    v
GET /auth/me
    |
    v
Authenticated User
    |
    v
/dashboard
```

After a successful login, the token is stored locally and the current user is retrieved from the backend.

## Token Storage

The frontend stores the access token through the token storage service.

The token is not manually added by individual components.

Instead, the Axios API client automatically adds:

```text
Authorization: Bearer <access_token>
```

to authenticated requests.

## Session Restoration

When the application starts:

```text
Application Start
      |
      v
Token Exists?
      |
      +-- No --> Anonymous Session
      |
      +-- Yes
             |
             v
        GET /auth/me
             |
             +-- Valid --> Restore User
             |
             +-- Invalid --> Remove Token
```

Invalid or expired tokens are removed automatically when session restoration fails.

## Registration Flow

```text
Registration Form
       |
       v
POST /auth/register
       |
       v
User Created
       |
       v
Redirect to /login
```

Automatic login after registration is not part of the current implementation.

## Protected Routes

The `/dashboard` route requires authentication.

Unauthenticated users are redirected to:

```text
/login
```

The route protection layer waits for authentication restoration before deciding whether access is allowed.

This prevents premature redirects while the application is checking an existing session.

## Authenticated Route Behavior

Authenticated users who access:

```text
/login
/register
```

are redirected to:

```text
/dashboard
```

## Logout Flow

```text
Logout
   |
   v
Remove JWT
   |
   v
Clear User State
   |
   v
Redirect to /login
```

## Error Handling

The frontend maps backend authentication errors to user-facing messages.

### Login

```text
401 -> Invalid email or password
403 -> Inactive user account
other -> Generic sign-in error
```

### Registration

```text
409 -> Email already registered
422 -> Invalid registration data
other -> Generic registration error
```

## Current Frontend Authentication Components

```text
src/api/auth.ts
src/api/client.ts
src/services/tokenStorage.ts
src/features/auth/AuthContext.tsx
src/features/auth/ProtectedRoute.tsx
src/pages/LoginPage.tsx
src/pages/RegisterPage.tsx
src/pages/DashboardPage.tsx
```

## Current Security Scope

The current implementation uses an access token stored in browser local storage.

This is sufficient for the current portfolio milestone, but future production hardening may include:

- Refresh tokens.
- HttpOnly cookies.
- Token rotation.
- Session revocation.
- CSRF protection where applicable.
- More advanced token expiration handling.

## Validation

The authentication flow validates:

- Registration.
- Login.
- JWT persistence.
- Authenticated Axios requests.
- `/auth/me` integration.
- Session restoration.
- Protected routes.
- Logout.
- Login error handling.
- Registration error handling.
- Frontend linting.
- Frontend formatting.
- Production build.

## Current Scope

The current implementation does not include:

- Password reset.
- Email verification.
- MFA.
- Social login.
- Refresh tokens.
- Remember-me behavior.
- Advanced session management.