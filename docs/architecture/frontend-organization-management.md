# Frontend Organization Management

The frontend organization management flow allows authenticated users to create, update, and delete organizations using the existing FastAPI organization endpoints.

The implementation builds on the existing authentication and organization context layers.

## Backend Endpoints

```text
GET    /organizations
POST   /organizations
GET    /organizations/{organization_id}
PATCH  /organizations/{organization_id}
DELETE /organizations/{organization_id}
```

## Frontend Responsibilities

The frontend organization management layer is responsible for:

- Creating organizations.
- Editing the active organization.
- Deleting the active organization.
- Handling organization validation errors.
- Handling authorization errors.
- Refreshing organization state after changes.
- Keeping the active organization synchronized.
- Falling back safely when an active organization is deleted.

## Organization API Client

The frontend organization API exposes:

```text
getOrganizations()
createOrganization()
updateOrganization()
deleteOrganization()
```

All requests use the shared authenticated Axios client.

## Organization Creation

The dashboard provides a form containing:

```text
name
slug
```

Creation flow:

```text
Create Organization Form
        |
        v
POST /organizations
        |
        v
Organization Created
        |
        v
Refresh Organization Context
        |
        v
Set Created Organization Active
```

The backend automatically assigns the authenticated creator as the organization owner.

## Organization Creation Validation

The frontend handles:

```text
409 -> Organization slug already exists
422 -> Invalid organization data
other -> Generic creation error
```

The slug input follows the backend slug rules:

```text
lowercase letters
numbers
hyphens
```

## Organization Update

The active organization can be updated through the dashboard.

Supported fields:

```text
name
slug
```

Update flow:

```text
Active Organization
        |
        v
Edit Form
        |
        v
PATCH /organizations/{organization_id}
        |
        v
Updated Organization
        |
        v
Refresh Organization Context
        |
        v
Keep Updated Organization Active
```

Because the backend uses `PATCH`, name and slug can be updated independently.

## Update Error Handling

The frontend handles:

```text
403 -> Insufficient permission
409 -> Organization slug already exists
422 -> Invalid organization data
other -> Generic update error
```

The backend currently allows organization updates for:

```text
owner
admin
```

Members without sufficient role receive an authorization error.

## Organization Deletion

Organization deletion is performed against the currently active organization.

Before sending the request, the frontend asks the user to confirm the destructive operation.

Deletion flow:

```text
Active Organization
        |
        v
Delete Confirmation
        |
        +-- Cancel -> No Action
        |
        +-- Confirm
                |
                v
DELETE /organizations/{organization_id}
                |
                v
Refresh Organization Context
                |
                +-- Other Organizations
                |       |
                |       v
                | Select Valid Organization
                |
                +-- No Organizations
                        |
                        v
                    Empty State
```

## Delete Authorization

Organization deletion is restricted by the backend to:

```text
owner
```

Admin and member roles cannot delete the organization.

The frontend handles authorization failures without altering local organization state.

## Delete Error Handling

The frontend handles:

```text
403 -> User cannot delete the organization
404 -> Organization not found
other -> Generic deletion error
```

## Organization Context Synchronization

After create, update, or delete operations, the frontend reloads the organization list through:

```text
refreshOrganizations()
```

The organization context then ensures that:

- The organization list reflects the backend state.
- The previously active organization remains active when still valid.
- A newly created organization can be selected immediately.
- An updated organization remains active.
- A deleted active organization is replaced by another available organization.
- If no organizations remain, the active organization becomes `null`.

## Active Organization Persistence

The active organization ID continues to be persisted in local storage.

When organizations are refreshed, the context checks whether the stored organization still exists.

If it does not, the first available organization becomes active.

## Dashboard Capabilities

The dashboard currently supports:

- Authenticated user information.
- Organization creation.
- Organization selection.
- Active organization display.
- Organization update.
- Organization deletion.
- Empty organization state.
- Loading states.
- API error states.
- Logout.

## Current Files

```text
src/types/organization.ts
src/api/organizations.ts
src/services/organizationStorage.ts
src/features/organizations/OrganizationContext.tsx
src/pages/DashboardPage.tsx
```

## Current Scope

The current implementation does not include:

- Member management UI.
- Invitation management UI.
- Ownership transfer.
- Organization settings.
- Billing.
- Soft deletion.
- Advanced confirmation dialogs.
- Advanced visual design system.

These capabilities can be implemented in later frontend milestones.