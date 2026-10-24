# Organization Update Flow

Organizations can be updated by authorized members with sufficient organization-level permissions.

The update flow builds on the existing authentication, membership, tenant authorization, and RBAC layers.

## Endpoint

```text
PATCH /organizations/{organization_id}
```

Authentication is required.

## Authorization

The user must:

- Be authenticated.
- Belong to the target organization.
- Have at least the `admin` role.

Role behavior:

```text
owner  -> allowed
admin  -> allowed
member -> denied
```

A user without membership in the target organization is also denied.

## Request

The endpoint supports partial updates.

Example:

```json
{
  "name": "Updated Organization Name"
}
```

Another example:

```json
{
  "slug": "updated-organization-slug"
}
```

Both fields can also be updated in the same request:

```json
{
  "name": "Updated Organization",
  "slug": "updated-organization"
}
```

## Partial Update

Because the endpoint uses `PATCH`, fields are optional.

Only values included in the request are changed.

Existing values remain unchanged when their corresponding fields are omitted.

## Name Validation

The organization name must:

- Be at least 2 characters long.
- Be at most 120 characters long.

## Slug Validation

The organization slug must:

- Be between 2 and 120 characters.
- Contain lowercase letters, numbers, and hyphens.
- Not contain spaces.
- Not contain uppercase letters.
- Not contain unsupported special characters.

Examples of valid slugs:

```text
acme
acme-corporation
company-123
```

## Slug Uniqueness

Organization slugs remain globally unique.

When updating a slug, the service checks whether another organization already uses the requested value.

The current organization is excluded from that duplicate check.

This allows an organization to retain its existing slug without creating a false conflict.

## Duplicate Slug Response

When another organization already owns the requested slug, the API returns:

```text
409 Conflict
```

with:

```json
{
  "detail": "Organization slug already exists"
}
```

## Successful Response

A successful update returns:

```text
200 OK
```

with the updated organization representation.

Example:

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "name": "Updated Organization",
  "slug": "updated-organization",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-02T12:00:00Z"
}
```

## Authorization Flow

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
OrganizationUpdateRequest
       |
       v
Organization Service
       |
       +-- Update name
       |
       +-- Validate slug uniqueness
       |
       +-- Update slug
       |
       v
Database Commit
```

## Cross-Organization Protection

Authorization is performed using the requested `organization_id`.

A user cannot update another organization unless they have the required membership and role in that organization.

The update service also operates only on the requested organization identifier.

## Membership Integrity

Updating an organization does not modify:

- Membership records.
- User roles.
- Membership statuses.
- Organization ownership.

Only organization fields within the current update scope are changed.

## Validation Errors

Invalid request data returns:

```text
422 Unprocessable Entity
```

Examples include:

- Invalid slug format.
- Name shorter than the minimum length.
- Name longer than the maximum length.
- Slug outside the configured length limits.

## Testing

The organization update flow includes tests for:

- Updating the organization name.
- Updating the organization slug.
- Duplicate slug rejection.
- Admin update access.
- Owner update access through RBAC hierarchy.
- Member update rejection.
- Invalid slug rejection.
- Organization isolation.

## Current Scope

The current implementation does not include:

- Organization deletion.
- Ownership transfer.
- Billing configuration.
- Custom organization settings.
- Invitation management.
- Custom permission models.
- Membership changes during organization updates.