import {
  createContext,
  type ReactNode,
  useContext,
  useEffect,
  useState,
} from "react"

import { getOrganizations } from "../../api/organizations"
import { useAuth } from "../auth/AuthContext"
import type { Organization } from "../../types/organization"

type OrganizationContextValue = {
  organizations: Organization[]
  activeOrganization: Organization | null
  isLoading: boolean
  error: string | null
  setActiveOrganization: (organization: Organization) => void
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

  useEffect(() => {
    async function loadOrganizations() {
      if (!isAuthenticated) {
        setOrganizations([])
        setActiveOrganizationState(null)
        setError(null)
        return
      }

      setIsLoading(true)
      setError(null)

      try {
        const result = await getOrganizations()

        setOrganizations(result)

        if (result.length > 0) {
          setActiveOrganizationState((current) => {
            if (
              current &&
              result.some(
                (organization) =>
                  organization.id === current.id,
              )
            ) {
              return current
            }

            return result[0]
          })
        } else {
          setActiveOrganizationState(null)
        }
      } catch {
        setOrganizations([])
        setActiveOrganizationState(null)
        setError("Unable to load organizations.")
      } finally {
        setIsLoading(false)
      }
    }

    void loadOrganizations()
  }, [isAuthenticated])

  function setActiveOrganization(
    organization: Organization,
  ): void {
    setActiveOrganizationState(organization)
  }

  return (
    <OrganizationContext.Provider
      value={{
        organizations,
        activeOrganization,
        isLoading,
        error,
        setActiveOrganization,
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