import {
  createContext,
  type ReactNode,
  useContext,
  useEffect,
  useState,
} from "react"

import {
  getActiveOrganizationId,
  removeActiveOrganizationId,
  setActiveOrganizationId,
} from "../../services/organizationStorage"

import { getOrganizations } from "../../api/organizations"
import { useAuth } from "../auth/AuthContext"
import type { Organization } from "../../types/organization"

type OrganizationContextValue = {
  organizations: Organization[]
  activeOrganization: Organization | null
  isLoading: boolean
  error: string | null
  setActiveOrganization: (organization: Organization) => void
  refreshOrganizations: () => Promise<void>
}

const OrganizationContext = createContext<
  OrganizationContextValue | undefined
>(undefined)

type OrganizationProviderProps = {
  children: ReactNode
}

export function OrganizationProvider({
  children,
}: OrganizationProviderProps) {
  const { isAuthenticated } = useAuth()

  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [activeOrganization, setActiveOrganizationState] =
    useState<Organization | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function refreshOrganizations(): Promise<void> {
    if (!isAuthenticated) {
      setOrganizations([])
      setActiveOrganizationState(null)
      setError(null)
      removeActiveOrganizationId()
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const result = await getOrganizations()

      setOrganizations(result)

      if (result.length > 0) {
        const storedOrganizationId =
          getActiveOrganizationId()

        const storedOrganization = result.find(
          (organization) =>
            organization.id === storedOrganizationId,
        )

        const organizationToActivate =
          storedOrganization ?? result[0]

        setActiveOrganizationState(
          organizationToActivate,
        )

        setActiveOrganizationId(
          organizationToActivate.id,
        )
      } else {
        setActiveOrganizationState(null)
        removeActiveOrganizationId()
      }
    } catch {
      setOrganizations([])
      setActiveOrganizationState(null)
      setError("Unable to load organizations.")
      removeActiveOrganizationId()
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void refreshOrganizations()
  }, [isAuthenticated])

  function setActiveOrganization(
    organization: Organization,
  ): void {
    setActiveOrganizationState(organization)
    setActiveOrganizationId(organization.id)
  }

  return (
    <OrganizationContext.Provider
      value={{
        organizations,
        activeOrganization,
        isLoading,
        error,
        setActiveOrganization,
        refreshOrganizations,
      }}
    >
      {children}
    </OrganizationContext.Provider>
  )
}

export function useOrganization(): OrganizationContextValue {
  const context = useContext(OrganizationContext)

  if (!context) {
    throw new Error(
      "useOrganization must be used inside OrganizationProvider",
    )
  }

  return context
}
