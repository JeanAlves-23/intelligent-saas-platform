import { useState, type FormEvent } from "react"
import { Navigate, useNavigate } from "react-router-dom"

import { registerUser } from "../api/auth"
import { useAuth } from "../features/auth/AuthContext"

export function RegisterPage() {
  const navigate = useNavigate()
  const { isAuthenticated, isLoading } = useAuth()

  const [fullName, setFullName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (isLoading) {
    return <p>Loading...</p>
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setError(null)
    setIsSubmitting(true)

    try {
      await registerUser({
        full_name: fullName,
        email,
        password,
      })

      navigate("/login", {
        replace: true,
      })
    } catch {
      setError(
        "Registration failed. Check the information and try again.",
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main>
      <h1>Create account</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="full-name">
            Full name
          </label>

          <input
            id="full-name"
            type="text"
            value={fullName}
            onChange={(event) =>
              setFullName(event.target.value)
            }
            required
            minLength={2}
            maxLength={150}
          />
        </div>

        <div>
          <label htmlFor="email">
            Email
          </label>

          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) =>
              setEmail(event.target.value)
            }
            required
          />
        </div>

        <div>
          <label htmlFor="password">
            Password
          </label>

          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
            required
            minLength={8}
            maxLength={128}
          />
        </div>

        {error && (
          <p role="alert">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting
            ? "Creating account..."
            : "Create account"}
        </button>
      </form>
    </main>
  )
}