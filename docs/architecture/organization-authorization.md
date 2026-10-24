# Organization-Scoped Authorization

Organization-scoped authorization ensures that authenticated users can only access organizations where they have an active membership relationship.

The authorization model is based on the existing `Membership` entity.

## Authorization Model

The access flow is:

```text
Authenticated User
       |
       v
Membership
       |
       v
Organization
```

A user does not gain access to an organization merely because the organization exists.

Access requires a matching membership between:

```text
user_id
organization_id
```

## Listing Accessible Organizations

The endpoint:

```text
GET /organizations
```

returns only organizations associated with the authenticated user's memberships.

The flow is:

```text
JWT
 |
 v
Current User
 |
 v
Membership Query
 |
 v
Accessible Organizations
```

If the user has no memberships, the endpoint returns an empty list.

## Accessing a Specific Organization

The endpoint:

```text
GET /organizations/{organization_id}
```

requires both:

- A valid authenticated user.
- A membership linking that user to the requested organization.

The authorization flow is:

```text
User + Organization ID
          |
          v
Membership Lookup
          |
     +----+----+
     |         |
    Found    Missing
     |         |
     v         v
   200 OK   403 Forbidden
```

## Reusable Authorization Dependency

Organization authorization is centralized in:

```text
app/api/dependencies/organization.py
```

The dependency:

```text
get_current_organization()
```

resolves the requested organization only when the current user has access.

This prevents authorization logic from being duplicated across future tenant-scoped endpoints.

## Service Layer

Organization membership resolution is implemented in:

```text
app/services/organization.py
```

The service exposes:

```text
get_user_organizations()
get_authorized_organization()
```

`get_user_organizations()` returns only organizations associated with the user.

`get_authorized_organization()` verifies access to a specific organization and raises an authorization error when no valid membership exists.

## Authorization Failures

A request to an organization without membership returns:

```text
403 Forbidden
```

with:

```json
{
  "detail": "Organization access denied"
}
```

Requests without valid authentication continue to return:

```text
401 Unauthorized
```

## Multi-Tenant Isolation

This authorization layer is the foundation for tenant data isolation.

Future organization-scoped resources will follow the same pattern:

```text
Authenticated User
       |
       v
Authorized Organization
       |
       v
Tenant-Scoped Resource
```

Examples may include:

```text
/organizations/{organization_id}/projects
/organizations/{organization_id}/members
/organizations/{organization_id}/settings
```

A resource should not be accessed until organization membership has been validated.

## Testing

Organization authorization tests cover:

- Listing only organizations associated with the current user.
- Returning an empty list when the user has no memberships.
- Rejecting unauthenticated requests.
- Accessing an organization with valid membership.
- Rejecting access without membership.
- Invalid organization identifiers.
- Reusable service-layer authorization behavior.

## Current Scope

The current implementation validates organization membership only.

It does not yet enforce:

- Membership roles.
- Role hierarchy.
- Fine-grained permissions.
- Resource-specific permissions.
- Organization invitation flows.
- Administrative privileges.

These capabilities can be layered on top of the organization authorization foundation.