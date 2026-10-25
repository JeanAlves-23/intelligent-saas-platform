import { useNavigate } from "react-router-dom"

import { useAuth } from "../features/auth/AuthContext"

export function DashboardPage() {
  const navigate = useNavigate()
  const {
    user,
    logout,
  } = useAuth()

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
        <>
          <p>
            Signed in as {user.full_name}
          </p>

          <p>{user.email}</p>
        </>
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