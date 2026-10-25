# Organization Invitation Flow

Organizations can invite users to join through a secure invitation workflow.

The invitation system builds on the existing authentication, organization membership, RBAC, and multi-tenant authorization layers.

## Invitation Creation Endpoint

```text
POST /organizations/{organization_id}/invitations
```

Authentication is required.

## Authorization

Invitation creation requires at least the `admin` role.

Role behavior:

```text
owner  -> allowed
admin  -> allowed
member -> denied
```

Role assignment rules:

```text
owner -> can invite admin or member
admin -> can invite member
```

The `owner` role cannot be assigned through invitations in the current implementation.

## Invitation Request

Example:

```json
{
  "email": "new.user@example.com",
  "role": "member"
}
```

The invited email is normalized before persistence.

## Invitation Model

An invitation stores:

- Organization ID.
- Invited email.
- Intended role.
- Secure invitation token.
- Expiration timestamp.
- Acceptance timestamp.
- Creation timestamp.

## Secure Token Generation

Invitation tokens are generated using Python's cryptographically secure `secrets` module.

Conceptually:

```python
secrets.token_urlsafe(32)
```

Tokens are unique and are not based on predictable database identifiers.

## Invitation Expiration

Invitations are created with a limited validity period.

The current implementation uses:

```text
7 days
```

Expired invitations cannot be accepted.

## Duplicate Invitations

The system prevents multiple active invitations for the same email and organization.

An active invitation is one that:

- Has not been accepted.
- Has not expired.

Attempting to create another active invitation returns:

```text
409 Conflict
```

## Existing Members

Users who already belong to the organization cannot be invited again.

The API returns:

```text
409 Conflict
```

with:

```json
{
  "detail": "User is already an organization member"
}
```

## Invitation Acceptance Endpoint

```text
POST /invitations/{token}/accept
```

The invited user must be authenticated.

## Acceptance Flow

```text
Authenticated User
       |
       v
Invitation Token
       |
       v
Invitation Exists?
       |
       v
Already Accepted?
       |
       v
Expired?
       |
       v
Email Matches?
       |
       v
Already a Member?
       |
       v
Create Membership
       +
Set accepted_at
       |
       v
Single Database Commit
```

## Email Validation

The authenticated user's email must match the email stored in the invitation.

A different authenticated user cannot accept the invitation.

If the email does not match, the API returns:

```text
403 Forbidden
```

## Expired Invitations

An expired invitation returns:

```text
410 Gone
```

with:

```json
{
  "detail": "Invitation expired"
}
```

## Already Accepted Invitations

An invitation cannot be reused after successful acceptance.

Reusing it returns:

```text
409 Conflict
```

with:

```json
{
  "detail": "Invitation already accepted"
}
```

## Missing Invitations

An invalid or unknown invitation token returns:

```text
404 Not Found
```

## Membership Creation

When a valid invitation is accepted, a new membership is created using:

- The authenticated user's ID.
- The invitation's organization ID.
- The role stored in the invitation.

The invitation is marked as accepted in the same transaction.

This keeps membership creation and invitation consumption atomic.

## Multi-Tenant Protection

Invitation creation is scoped to the organization specified in the request.

The inviter must have a valid membership and sufficient role in that organization.

Invitation acceptance also creates membership only for the organization referenced by the invitation.

## Testing

The invitation flow includes tests for:

- Owner creating member invitations.
- Owner creating admin invitations.
- Admin creating member invitations.
- Admin being prevented from inviting admins.
- Member being prevented from creating invitations.
- Owner role being rejected as an invitation role.
- Duplicate active invitations.
- Existing-member invitation rejection.
- Successful invitation acceptance.
- Invitation email mismatch.
- Expired invitations.
- Already accepted invitations.
- Invalid invitation tokens.
- Existing-member acceptance rejection.
- Authentication requirements.
- Membership creation after acceptance.

## Current Scope

The current implementation does not include:

- Sending real invitation emails.
- Email provider integration.
- Invitation resend.
- Invitation revocation.
- Reminder notifications.
- Ownership transfer.
- Public registration through invitation links.
- Bulk invitations.
- Organization domain restrictions.
- Custom roles.

These capabilities can be added later as the platform evolves.