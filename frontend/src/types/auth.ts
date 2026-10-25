export type User = {
    id: string
    email: string
    full_name: string
    is_active: boolean
    created_at: string
    updated_at: string
}

export type LoginRequest = {
    email: string
    password: string
}

export type LoginResponse = {
    access_token: string
    token_type: string
}

export type RegisterRequest = {
    email: string
    full_name: string
    password: string
}
