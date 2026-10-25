import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

import App from "./App"
import { AuthProvider } from "./features/auth/AuthContext"
import { OrganizationProvider } from "./features/organizations/OrganizationContext"
import "./index.css"

const queryClient = new QueryClient()

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <QueryClientProvider client={queryClient}>
            <AuthProvider>
                <OrganizationProvider>
                    <App />
                </OrganizationProvider>
            </AuthProvider>
        </QueryClientProvider>
    </StrictMode>,
)
