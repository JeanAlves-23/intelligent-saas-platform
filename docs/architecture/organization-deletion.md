# Organization Deletion Flow

Organizations can be permanently deleted by authorized owners.

The deletion flow builds on the existing authentication, membership, tenant authorization, RBAC, and database integrity layers.

## Endpoint

```text
DELETE /organizations/{organization_id}
```

Authentication is required.

## Authorization

The user must:

- Be authenticated.
- Belong to the target organization.
- Have the `owner` role.

Role behavior:

```text
owner  -> allowed
admin  -> denied
member -> denied
```

A user without membership in the requested organization is also denied.

## Successful Response

A successful deletion returns:

```text
204 No Content
```

No response body is returned.

## Deletion Flow

```text
Authenticated User
       |
       v
Organization Membership
       |
       v
RBAC == owner
       |
       v
Organization Service
       |
       v
Delete Organization
       |
       v
Database Commit
       |
       v
ON DELETE CASCADE
       |
       v
Associated Memberships Removed
```

## Membership Cleanup

Memberships reference organizations through a foreign key configured with:

```text
ON DELETE CASCADE
```

When an organization is deleted, PostgreSQL automatically removes its associated membership records.

This prevents orphaned memberships and keeps tenant data consistent.

## Database Integrity

The organization deletion service removes the organization and commits the transaction.

Membership cleanup is delegated to the database foreign key constraint rather than being implemented manually in the service layer.

This keeps referential integrity enforced at the database level.

## SQLAlchemy Session State

Database-level cascades happen directly inside PostgreSQL.

Because SQLAlchemy may still have previously loaded membership objects in its session identity map, tests that verify cascade deletion may need to expire the session state before querying again.

For example:

```python
db.expire_all()
```

This forces SQLAlchemy to read the current database state instead of returning a cached ORM object.

## Authorization Isolation

The deletion endpoint authorizes access using the requested `organization_id`.

A user cannot delete an organization unless they have an owner membership for that organization.

Users without access receive an authorization failure before the deletion service is executed.

This avoids exposing organization data outside the current user's authorized tenant scope.

## Missing Organization

At the service layer, attempting to delete an organization that does not exist raises an organization-not-found error.

For requests that do not pass organization authorization, the API does not expose whether the target organization exists.

## Testing

The organization deletion flow includes tests for:

- Successful owner deletion.
- Database removal of the organization.
- Cascading membership deletion.
- Deletion of a nonexistent organization.
- Admin deletion rejection.
- Member deletion rejection.
- Tenant-scoped authorization.
- Database integrity after deletion.

## Current Scope

The current implementation performs permanent deletion.

It does not include:

- Soft deletion.
- Organization recovery.
- Ownership transfer.
- Audit log preservation.
- Billing cancellation.
- Data export.
- Organization archival.
- Future organization-owned resource cleanup beyond configured database cascades.

These capabilities can be added in later iterations as the platform domain expands.