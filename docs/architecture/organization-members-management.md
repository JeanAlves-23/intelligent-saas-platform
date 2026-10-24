# Organization Members Management

Organization membership management allows authorized users to inspect organization members and update membership roles.

The implementation builds on the existing organization authorization and RBAC foundations.

## Member Listing

The endpoint:

```text
GET /organizations/{organization_id}/members
```

returns memberships for the requested organization.

Access requires at least the `admin` role.

Expected behavior:

```text
owner  -> allowed
admin  -> allowed
member -> denied
```

The response includes:

```text
membership id
organization id
role
status
created_at
updated_at
user
```

The nested user representation includes:

```text
id
email
full_name
is_active
```

Sensitive fields such as:

```text
password_hash
```

are never exposed.

## Role Updates

The endpoint:

```text
PATCH /organizations/{organization_id}/members/{membership_id}
```

allows an organization owner to change a membership role.

Example request:

```json
{
  "role": "admin"
}
```

Supported roles are:

```text
owner
admin
member
```

Only users with the `owner` role can perform membership role updates.

Expected behavior:

```text
owner  -> allowed
admin  -> denied
member -> denied
```

## Cross-Organization Protection

Membership updates are scoped by both:

```text
organization_id
membership_id
```

A membership from another organization cannot be modified through the requested organization context.

If the membership does not belong to the organization, the API returns:

```text
404 Not Found
```

with:

```json
{
  "detail": "Membership not found"
}
```

## Authorization Flow

Member listing:

```text
Authenticated User
       |
       v
Organization Membership
       |
       v
RBAC >= admin
       |
       v
Organization Members
```

Role update:

```text
Authenticated User
       |
       v
Organization Membership
       |
       v
RBAC >= owner
       |
       v
Target Membership
       |
       v
Role Update
```

## Service Layer

Membership management logic is centralized in:

```text
app/services/membership.py
```

The service exposes:

```text
list_organization_members()
update_membership_role()
```

This keeps database access and organization-scoping rules outside the API route layer.

## Schemas

Membership API schemas are defined in:

```text
app/schemas/membership.py
```

They provide safe serialization for membership and nested user data.

## Testing

The membership management flow includes tests for:

- Admin listing organization members.
- Member rejection when listing members.
- Owner updating membership roles.
- Admin rejection when updating roles.
- Cross-organization membership protection.
- Role validation.
- Safe membership serialization.
- Service-layer organization isolation.

## Current Scope

The current implementation does not include:

- Inviting users
- Removing members
- Ownership transfer workflows
- Single-owner enforcement
- Custom roles
- Fine-grained permissions
- Membership invitations
- Email notifications

These capabilities can be implemented in later iterations.