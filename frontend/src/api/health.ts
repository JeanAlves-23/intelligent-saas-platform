import { api } from "./client"

export type HealthResponse = {
    status: string
}

export async function getHealth(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>("/health")
    return response.data
}
