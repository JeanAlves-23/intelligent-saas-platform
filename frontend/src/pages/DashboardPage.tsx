import axios from "axios"
import { useState, type FormEvent } from "react"
import { useNavigate } from "react-router-dom"

import { createOrganization } from "../api/organizations"
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
    refreshOrganizations,
  } = useOrganization()

  const [name, setName] = useState("")
  const [slug, setSlug] = useState("")
  const [createError, setCreateError] = useState<string | null>(null)
  const [isCreating, setIsCreating] = useState(false)

  function handleLogout() {
    logout()

    navigate("/login", {
      replace: true,
    })
  }

  async function handleCreateOrganization(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setCreateError(null)
    setIsCreating(true)

    try {
      const organization = await createOrganization({
        name,
        slug,
      })

      await refreshOrganizations()

      setActiveOrganization(organization)

      setName("")
      setSlug("")
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status

        if (status === 409) {
          setCreateError("This organization slug is already in use.")
        } else if (status === 422) {
          setCreateError("Please check the organization information.")
        } else {
          setCreateError("Unable to create organization.")
        }
      } else {
        setCreateError("Unable to create organization.")
      }
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <main>
      <h1>Dashboard</h1>

      {user && (
        <section>
          <h2>Account</h2>

          <p>Signed in as {user.full_name}</p>
          <p>{user.email}</p>
        </section>
      )}

      <section>
        <h2>Create Organization</h2>

        <form onSubmit={handleCreateOrganization}>
          <div>
            <label htmlFor="organization-name">
              Organization name
            </label>

            <input
              id="organization-name"
              type="text"
              value={name}
              onChange={(event) =>
                setName(event.target.value)
              }
              minLength={2}
              maxLength={120}
              required
            />
          </div>

          <div>
            <label htmlFor="organization-slug">
              Slug
            </label>

            <input
              id="organization-slug"
              type="text"
              value={slug}
              onChange={(event) =>
                setSlug(event.target.value)
              }
              minLength={2}
              maxLength={120}
              pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
              required
            />
          </div>

          {createError && (
            <p role="alert">
              {createError}
            </p>
          )}

          <button
            type="submit"
            disabled={isCreating}
          >
            {isCreating
              ? "Creating..."
              : "Create organization"}
          </button>
        </form>
      </section>

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