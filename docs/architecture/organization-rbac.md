# Organization Role-Based Authorization

Organization RBAC controls what an authenticated member can do inside an organization based on their membership role.

The current role hierarchy is:

```text
owner  >  admin  >  member
```

## Roles

Supported organization roles are defined centrally in:

```text
app/core/roles.py
```

The current roles are:

```text
owner
admin
member
```

Their effective hierarchy is:

```text
owner  = 3
admin  = 2
member = 1
```

This means:

```text
owner  can satisfy owner, admin, and member requirements
admin  can satisfy admin and member requirements
member can satisfy member requirements only
```

## Membership-Based Authorization

RBAC is evaluated only after organization membership is established.

The authorization flow is:

```text
Authenticated User
       |
       v
Membership
       |
       v
Organization
       |
       v
Membership.role
       |
       v
Role Requirement
       |
   +---+---+
   |       |
 Allowed  Denied
   |       |
   v       v
 200     403
```

A user without membership is denied before role validation.

## Reusable Role Authorization

Role validation is implemented in:

```text
app/services/authorization.py
```

The service provides:

```text
has_required_role()
require_role()
```

`has_required_role()` evaluates whether the current role satisfies the required role.

`require_role()` raises an authorization error when the role is insufficient.

## API Dependency

Organization role enforcement is centralized in:

```text
app/api/dependencies/authorization.py
```

The reusable dependency factory:

```text
require_organization_role()
```

can be configured with the minimum role required by an endpoint.

Example:

```text
require_organization_role(OrganizationRole.ADMIN)
```

This permits:

```text
owner
admin
```

and rejects:

```text
member
```

## Authorization Failures

A user without membership receives:

```text
403 Forbidden
```

with:

```json
{
  "detail": "Organization access denied"
}
```

A member with an insufficient role receives:

```text
403 Forbidden
```

with:

```json
{
  "detail": "Insufficient organization role"
}
```

## Validation Endpoint

The current RBAC validation endpoint is:

```text
GET /organizations/{organization_id}/admin-check
```

It requires at least the `admin` role.

Expected behavior:

```text
owner  -> 200 OK
admin  -> 200 OK
member -> 403 Forbidden
no membership -> 403 Forbidden
```

This endpoint currently serves as a validation surface for the RBAC foundation.

Future domain endpoints will use the same reusable dependency instead of duplicating authorization logic.

## Testing

RBAC tests cover:

- Owner access to admin-level operations.
- Admin access to admin-level operations.
- Member rejection from admin-level operations.
- Rejection when no membership exists.
- Role hierarchy behavior.
- Unknown roles.
- Insufficient-role exceptions.

## Current Scope

The current RBAC implementation uses a fixed role hierarchy.

It does not yet support:

- Custom roles
- Fine-grained permissions
- Permission matrices
- Per-resource permissions
- Global administrators
- Billing permissions
- Dynamic role configuration

These capabilities can be introduced later without changing the basic membership-based authorization model.