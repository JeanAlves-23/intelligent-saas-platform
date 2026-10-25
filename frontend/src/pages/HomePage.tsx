import { useQuery } from "@tanstack/react-query"

import { getHealth } from "../api/health"

export function HomePage() {
    const healthQuery = useQuery({
        queryKey: ["health"],
        queryFn: getHealth,
    })

    return (
        <main>
            <h1>Intelligent SaaS Platform</h1>

            {healthQuery.isPending && <p>Checking backend...</p>}

            {healthQuery.isError && <p>Backend connection failed.</p>}

            {healthQuery.data && (
                <p>Backend status: {healthQuery.data.status}</p>
            )}
        </main>
    )
}
