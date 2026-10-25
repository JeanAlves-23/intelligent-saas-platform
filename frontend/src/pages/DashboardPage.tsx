import axios from "axios"
import { useState, type FormEvent } from "react"
import { useNavigate } from "react-router-dom"

import { useAuth } from "../features/auth/AuthContext"
import { useOrganization } from "../features/organizations/OrganizationContext"

import {
  createOrganization,
  deleteOrganization,
  updateOrganization,
} from "../api/organizations"


const [editName, setEditName] = useState("")
const [editSlug, setEditSlug] = useState("")
const [editError, setEditError] = useState<string | null>(null)
const [isUpdating, setIsUpdating] = useState(false)
const [deleteError, setDeleteError] = useState<string | null>(null)
const [isDeleting, setIsDeleting] = useState(false)

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

  async function handleUpdateOrganization(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (!activeOrganization) {
      return
    }

    setEditError(null)
    setIsUpdating(true)

    try {
      const updated = await updateOrganization(
        activeOrganization.id,
        {
          name: editName || activeOrganization.name,
          slug: editSlug || activeOrganization.slug,
        },
      )

      await refreshOrganizations()
      setActiveOrganization(updated)

      setEditName("")
      setEditSlug("")
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status

        if (status === 409) {
          setEditError("This organization slug is already in use.")
        } else if (status === 422) {
          setEditError("Please check the organization information.")
        } else if (status === 403) {
          setEditError("You do not have permission to update this organization.")
        } else {
          setEditError("Unable to update organization.")
        }
      } else {
        setEditError("Unable to update organization.")
      }
    } finally {
      setIsUpdating(false)
    }
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

  async function handleDeleteOrganization() {
    if (!activeOrganization) {
      return
    }

    const confirmed = window.confirm(
      `Delete organization "${activeOrganization.name}"? This action cannot be undone.`,
    )

    if (!confirmed) {
      return
    }

    setDeleteError(null)
    setIsDeleting(true)

    try {
      await deleteOrganization(activeOrganization.id)

      await refreshOrganizations()
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status

        if (status === 403) {
          setDeleteError(
            "You do not have permission to delete this organization.",
          )
        } else if (status === 404) {
          setDeleteError("Organization not found.")
        } else {
          setDeleteError("Unable to delete organization.")
        }
      } else {
        setDeleteError("Unable to delete organization.")
      }
    } finally {
      setIsDeleting(false)
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
        <><section>
          <h2>Active Organization</h2>

          <p>
            Name: {activeOrganization.name}
          </p>

          <p>
            Slug: {activeOrganization.slug}
          </p>
        </section>
        <section>
          <h2>Edit Organization</h2>

          <form onSubmit={handleUpdateOrganization}>
            <div>
              <label htmlFor="edit-organization-name">
                Name
              </label>

              <input
                id="edit-organization-name"
                type="text"
                value={editName}
                placeholder={activeOrganization.name}
                onChange={(event) => setEditName(event.target.value)}
                minLength={2}
                maxLength={120}
              />
            </div>

            <div>
              <label htmlFor="edit-organization-slug">
                Slug
              </label>

              <input
                id="edit-organization-slug"
                type="text"
                value={editSlug}
                placeholder={activeOrganization.slug}
                onChange={(event) => setEditSlug(event.target.value)}
                minLength={2}
                maxLength={120}
                pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
              />
            </div>

            {editError && (
              <p role="alert">
                {editError}
              </p>
            )}

            <button
              type="submit"
              disabled={isUpdating}
            >
              {isUpdating
                ? "Updating..."
                : "Update organization"}
            </button>
          </form>
        </section>
        <section>
        <h2>Delete Organization</h2>

        <p>
          Deleting an organization is permanent and cannot be undone.
        </p>

        {deleteError && (
          <p role="alert">
            {deleteError}
          </p>
        )}

        <button
          type="button"
          onClick={handleDeleteOrganization}
          disabled={isDeleting}
        >
          {isDeleting
            ? "Deleting..."
            : "Delete organization"}
        </button>
      </section></>
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