# Organization Domain

The `Organization` entity represents a tenant within the SaaS platform.

It is the root entity for multi-tenant data isolation and will be associated with users, memberships, projects, and other tenant-scoped resources in later iterations.

## Entity

The `Organization` model contains:

- `id`: UUID primary key.
- `name`: Human-readable organization name.
- `slug`: Unique organization identifier used for routing and references.
- `created_at`: Timestamp automatically generated when the organization is created.
- `updated_at`: Timestamp automatically maintained when the organization is updated.

## Multi-Tenancy

The application follows an organization-based multi-tenant model.

Future tenant-scoped resources will reference an organization to ensure that data belonging to one tenant remains isolated from other tenants.

A user will not be directly owned by a single organization.

Instead, future membership entities will associate users with organizations.

Conceptually:

```text
Organization
    |
    +-- Membership
           |
           +-- User