# User and Membership Domain

The platform separates user identity from organization membership.

A `User` represents a person with an account in the platform.

A `Membership` represents the relationship between a user and an organization.

This design allows the same user to participate in multiple organizations.

## User

The `User` entity contains:

- `id`: UUID primary key.
- `email`: Required and unique email address.
- `full_name`: Required display name.
- `is_active`: Indicates whether the user account is active.
- `created_at`: Timestamp automatically generated when the user is created.
- `updated_at`: Timestamp automatically maintained when the user is updated.

## Membership

The `Membership` entity contains:

- `id`: UUID primary key.
- `user_id`: Foreign key referencing `users.id`.
- `organization_id`: Foreign key referencing `organizations.id`.
- `role`: Role of the user within the organization.
- `status`: Membership status.
- `created_at`: Timestamp automatically generated when the membership is created.
- `updated_at`: Timestamp automatically maintained when the membership is updated.

## Relationship

Conceptually:

```text
User
  |
  +-- Membership
         |
         +-- Organization