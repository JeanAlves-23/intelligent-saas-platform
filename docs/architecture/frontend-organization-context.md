# Frontend Organization Context

The frontend organization context provides shared access to the authenticated user's organizations and the currently active organization.

It builds on the existing authentication session and organization API.

## Backend Endpoint

```text
GET /organizations
```

The request is authenticated automatically through the Axios JWT interceptor.

## Organization Context Responsibilities

The organization context is responsible for:

- Loading organizations for the authenticated user.
- Exposing the organization list.
- Selecting an active organization.
- Persisting the active organization locally.
- Restoring the active organization after page reload.
- Clearing organization state after logout.
- Providing loading and error states.

## Context State

The context exposes:

```text
organizations
activeOrganization
isLoading
error
setActiveOrganization()
```

## Loading Flow

```text
Authenticated User
       |
       v
GET /organizations
       |
       v
Organization List
       |
       +-- Empty
       |      |
       |      v
       |   Empty State
       |
       +-- Available Organizations
              |
              v
       Restore Stored Selection
              |
              +-- Found -> Use Stored Organization
              |
              +-- Missing -> Use First Organization
```

## Organization Selection

Users can select an active organization from the dashboard.

When an organization is selected:

```text
Organization Selected
        |
        v
Update Context State
        |
        v
Store Organization ID
        |
        v
localStorage
```

The selected organization remains active after a browser refresh.

## Persistence

The active organization ID is stored locally under:

```text
active_organization_id
```

Only the ID is persisted.

The full organization object is always restored from the latest `GET /organizations` response.

This prevents stale organization data from being stored permanently in the browser.

## Invalid Stored Organization

If the locally stored organization ID no longer belongs to the authenticated user, the frontend falls back to the first available organization.

The new organization ID is then persisted.

## Logout Behavior

When the user logs out:

- Organization list is cleared.
- Active organization is cleared.
- Stored organization ID is removed.
- Organization errors are cleared.

This prevents one user's organization selection from affecting another authenticated session.

## Dashboard

The dashboard currently displays:

- Authenticated user's name.
- Authenticated user's email.
- Available organizations.
- Active organization selector.
- Active organization name.
- Active organization slug.
- Logout action.

## Empty State

If the authenticated user does not belong to any organizations, the dashboard displays an empty state rather than an organization selector.

Organization creation is intentionally outside the current issue scope.

## Error Handling

If the organization API request fails:

```text
Unable to load organizations.
```

is exposed through the organization context and displayed by the dashboard.

The current organization state is cleared when loading fails.

## Provider Hierarchy

The frontend provider hierarchy is:

```text
QueryClientProvider
        |
        v
AuthProvider
        |
        v
OrganizationProvider
        |
        v
Application
```

`OrganizationProvider` is nested inside `AuthProvider` because organization loading depends on the current authentication state.

## Current Files

```text
src/types/organization.ts
src/api/organizations.ts
src/services/organizationStorage.ts
src/features/organizations/OrganizationContext.tsx
src/pages/DashboardPage.tsx
```

## Future Usage

The active organization context will support organization-scoped frontend features such as:

- Member management.
- Invitations.
- Organization settings.
- Role-aware navigation.
- Organization-specific dashboards.
- Future SaaS resources.

## Current Scope

The current implementation does not include:

- Organization creation UI.
- Organization editing UI.
- Organization deletion UI.
- Member management UI.
- Invitation management UI.
- Server-side persistence of the user's preferred organization.
- Organization analytics.
- Advanced dashboard design.