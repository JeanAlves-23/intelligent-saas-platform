import { api } from "./client"
import type { Organization } from "../types/organization"

export async function getOrganizations(): Promise<Organization[]> {
  const response = await api.get<Organization[]>("/organizations")

  return response.data
}