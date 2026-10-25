export type Organization = {
  id: string
  name: string
  slug: string
  created_at: string
  updated_at: string
}

export type OrganizationCreateRequest = {
  name: string
  slug: string
}

export type OrganizationUpdateRequest = {
  name?: string
  slug?: string
}