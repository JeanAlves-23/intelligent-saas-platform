# Authentication Foundation

The authentication foundation is responsible for secure password handling and password persistence.

The current implementation intentionally focuses only on password hashing and verification.

Authentication endpoints, tokens, sessions, and authorization will be introduced in later iterations.

## Password Hashing

Plain-text passwords must never be stored in the database.

The application uses Argon2 password hashing through `pwdlib`.

The password flow is:

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