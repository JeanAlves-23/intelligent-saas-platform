import { api } from "./client"
import type {
  Organization,
  OrganizationCreateRequest,
  OrganizationUpdateRequest,
} from "../types/organization"

export async function getOrganizations(): Promise<Organization[]> {
  const response = await api.get<Organization[]>("/organizations")

  return response.data
}

export async function createOrganization(
  payload: OrganizationCreateRequest,
): Promise<Organization> {
  const response = await api.post<Organization>(
    "/organizations",
    payload,
  )

  return response.data
}

export async function updateOrganization(
  organizationId: string,
  payload: OrganizationUpdateRequest,
): Promise<Organization> {
  const response = await api.patch<Organization>(
    `/organizations/${organizationId}`,
    payload,
  )

  return response.data
}

export async function deleteOrganization(
  organizationId: string,
): Promise<void> {
  await api.delete(`/organizations/${organizationId}`)
}