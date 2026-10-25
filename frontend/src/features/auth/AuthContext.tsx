import {
  createContext,
  type ReactNode,
  useContext,
  useEffect,
  useState,
} from "react"

import {
  getCurrentUser,
  loginUser,
} from "../../api/auth"
import {
  getAccessToken,
  removeAccessToken,
  setAccessToken,
} from "../../services/tokenStorage"
import type {
  LoginRequest,
  User,
} from "../../types/auth"

type AuthContextValue = {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (payload: LoginRequest) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(
  undefined,
)

type AuthProviderProps = {
  children: ReactNode
}

export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function restoreSession() {
      const token = getAccessToken()

      if (!token) {
        setIsLoading(false)
        return
      }

      try {
        const currentUser = await getCurrentUser()
        setUser(currentUser)
      } catch {
        removeAccessToken()
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }

    void restoreSession()
  }, [])

  async function login(
    payload: LoginRequest,
  ): Promise<void> {
    const result = await loginUser(payload)

    setAccessToken(result.access_token)

    try {
      const currentUser = await getCurrentUser()
      setUser(currentUser)
    } catch (error) {
      removeAccessToken()
      throw error
    }
  }

  function logout(): void {
    removeAccessToken()
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: user !== null,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider",
    )
  }

  return context
}