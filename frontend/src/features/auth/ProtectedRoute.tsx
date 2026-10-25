import type { ReactNode } from "react"
import { Navigate, useLocation } from "react-router-dom"

import { useAuth } from "./AuthContext"

type ProtectedRouteProps = {
    children: ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
    const location = useLocation()
    const { isAuthenticated, isLoading } = useAuth()

    if (isLoading) {
        return <p>Loading...</p>
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace state={{ from: location }} />
    }

    return children
}
