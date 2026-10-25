import { useNavigate } from "react-router-dom"

import { useAuth } from "../features/auth/AuthContext"
import { useOrganization } from "../features/organizations/OrganizationContext"

export function DashboardPage() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const {
    organizations,
    activeOrganization,
    isLoading,
    error,
    setActiveOrganization,
  } = useOrganization()

  function handleLogout() {
    logout()

    navigate("/login", {
      replace: true,
    })
  }

  return (
    <main>
      <h1>Dashboard</h1>

      {user && (
        <section>
          <h2>Account</h2>

          <p>
            Signed in as {user.full_name}
          </p>

          <p>{user.email}</p>
        </section>
      )}

      <section>
        <h2>Organizations</h2>

        {isLoading && (
          <p>Loading organizations...</p>
        )}

        {error && (
          <p role="alert">
            {error}
          </p>
        )}

        {!isLoading &&
          !error &&
          organizations.length === 0 && (
            <p>
              You do not belong to any organizations yet.
            </p>
          )}

        {!isLoading &&
          !error &&
          organizations.length > 0 && (
            <>
              <label htmlFor="organization">
                Active organization
              </label>

              <select
                id="organization"
                value={activeOrganization?.id ?? ""}
                onChange={(event) => {
                  const organization =
                    organizations.find(
                      (item) =>
                        item.id === event.target.value,
                    )

                  if (organization) {
                    setActiveOrganization(organization)
                  }
                }}
              >
                {organizations.map((organization) => (
                  <option
                    key={organization.id}
                    value={organization.id}
                  >
                    {organization.name}
                  </option>
                ))}
              </select>
            </>
          )}
      </section>

      {activeOrganization && (
        <section>
          <h2>Active Organization</h2>

          <p>
            Name: {activeOrganization.name}
          </p>

          <p>
            Slug: {activeOrganization.slug}
          </p>
        </section>
      )}

      <button
        type="button"
        onClick={handleLogout}
      >
        Logout
      </button>
    </main>
  )
}