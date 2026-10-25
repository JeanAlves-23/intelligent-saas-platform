import { useAuth } from "../features/auth/AuthContext"

export function DashboardPage() {
  const {
    user,
    logout,
  } = useAuth()

  return (
    <main>
      <h1>Dashboard</h1>

      {user && (
        <>
          <p>
            Signed in as {user.full_name}
          </p>

          <p>{user.email}</p>
        </>
      )}

      <button
        type="button"
        onClick={logout}
      >
        Logout
      </button>
    </main>
  )
}