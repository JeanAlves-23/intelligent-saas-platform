import axios from "axios"
import { useState, type FormEvent } from "react"
import { Navigate, useNavigate } from "react-router-dom"

import { useAuth } from "../features/auth/AuthContext"

export function LoginPage() {
    const navigate = useNavigate()
    const { login, isAuthenticated, isLoading } = useAuth()

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

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()

        setError(null)
        setIsSubmitting(true)

        try {
            await login({
                email,
                password,
            })

            navigate("/dashboard", {
                replace: true,
            })
        } catch (error) {
            if (axios.isAxiosError(error)) {
                const status = error.response?.status

                if (status === 409) {
                    setError("This email is already registered.")
                } else if (status === 422) {
                    setError("Please check the registration information.")
                } else {
                    setError("Unable to create the account. Please try again.")
                }
            } else {
                setError("Unable to create the account. Please try again.")
            }
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <main>
            <h1>Login</h1>

            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="email">Email</label>

                    <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        required
                    />
                </div>

                <div>
                    <label htmlFor="password">Password</label>

                    <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                        required
                        minLength={8}
                    />
                </div>

                {error && <p role="alert">{error}</p>}

                <button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? "Signing in..." : "Sign in"}
                </button>
            </form>
        </main>
    )
}
