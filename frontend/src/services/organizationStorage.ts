const ACTIVE_ORGANIZATION_KEY = "active_organization_id"

export function getActiveOrganizationId(): string | null {
  return localStorage.getItem(ACTIVE_ORGANIZATION_KEY)
}

export function setActiveOrganizationId(
  organizationId: string,
): void {
  localStorage.setItem(
    ACTIVE_ORGANIZATION_KEY,
    organizationId,
  )
}

export function removeActiveOrganizationId(): void {
  localStorage.removeItem(ACTIVE_ORGANIZATION_KEY)
}