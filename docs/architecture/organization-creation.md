# Organization Creation Flow

Authenticated users can create new organizations through the API.

When an organization is created successfully, the authenticated user automatically becomes its `owner`.

## Endpoint

```text
POST /organizations
```

Authentication is required.

## Request

Example request:

```json
{
  "name": "Acme Corporation",
  "slug": "acme-corporation"
}
```

The organization name and slug are validated before persistence.

## Slug Rules

The slug must:

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

## Creation Flow

The creation process is:

```text
Authenticated User
       |
       v
OrganizationCreateRequest
       |
       v
Organization Service
       |
       +-- Validate duplicate slug
       |
       +-- Create Organization
       |
       +-- Flush Organization ID
       |
       +-- Create Membership
       |      role = owner
       |
       v
Single Database Commit
```

## Automatic Owner Membership

The user creating the organization receives a membership with:

```text
role = owner
status = active
```

This immediately gives the creator access to the organization through the existing membership and RBAC authorization layers.

## Atomic Transaction

Organization creation and owner membership creation are committed together.

The service first creates the organization and flushes the database session so that the organization ID becomes available.

It then creates the owner membership.

Only after both operations succeed is the transaction committed.

Conceptually:

```text
Create Organization
       |
       v
Create Owner Membership
       |
       v
Commit
```

If persistence fails before the final commit:

```text
Rollback
```

prevents partial organization creation.

## Duplicate Slugs

Organization slugs are unique.

When a duplicate slug is requested, the API returns:

```text
409 Conflict
```

with:

```json
{
  "detail": "Organization slug already exists"
}
```

The database unique constraint remains the final protection against duplicate slugs.

## Successful Response

Successful creation returns:

```text
201 Created
```

with the safe organization representation:

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "name": "Acme Corporation",
  "slug": "acme-corporation",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z"
}
```

## Integration With Organization Access

Because the creator automatically becomes an owner, the new organization immediately becomes available through:

```text
GET /organizations
```

and organization-scoped endpoints can authorize the creator through the existing membership and RBAC layers.

## Validation Errors

Invalid request data returns:

```text
422 Unprocessable Entity
```

Examples include:

- Missing organization name.
- Missing slug.
- Invalid slug format.
- Name or slug outside configured length limits.

## Testing

The organization creation flow includes tests for:

- Successful organization creation.
- Automatic owner membership creation.
- Duplicate slug rejection.
- Invalid slug validation.
- Authentication requirement.
- Service-layer organization creation.
- Atomic organization and membership persistence.

## Current Scope

The current implementation does not include:

- Organization updates
- Organization deletion
- Ownership transfer
- Invitations
- Billing configuration
- Custom organization settings
- Multiple-owner policy enforcement

These capabilities can be implemented in later iterations.