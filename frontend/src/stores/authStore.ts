import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient } from '@/lib/api';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  mfa_enabled: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  mfaToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<any>;
  logout: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      mfaToken: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (username: string, password: string) => {
        set({ isLoading: true });
        try {
          const response: any = await apiClient.post('/auth/login', { username, password });

          if (response.requires_mfa) {
            set({ isLoading: false, mfaToken: response.mfa_token });
            return response;
          }

          // Token is stored in HTTP-only cookie by backend
          // Set user and isAuthenticated explicitly
          set({
            user: response.user,
            token: 'cookie', // Placeholder since token is in HTTP-only cookie
            isAuthenticated: true,
            isLoading: false,
          });

          return response;
        } catch (error: any) {
          // Clear auth state on login failure
          set({
            isLoading: false,
            isAuthenticated: false,
            user: null,
            token: null,
          });
          throw new Error(error.response?.data?.detail || 'Login failed');
        }
      },

      logout: async () => {
        try {
          // Call backend to clear HTTP-only cookie
          await apiClient.post('/auth/logout');
        } catch (error) {
          console.error('Logout error:', error);
          // Continue with logout even if backend call fails
        } finally {
          // Clear local state
          set({
            user: null,
            token: null,
            isAuthenticated: false,
          });
        }
      },

      setUser: (user: User) => {
        set({ user, isAuthenticated: user !== null });
      },
    }),
    {
      name: 'auth-storage',
      // Only persist user and token, not isAuthenticated
      // isAuthenticated is derived from user on hydration
      partialize: (state) => ({
        user: state.user,
        token: state.token,
      }),
      onRehydrateStorage: () => (state) => {
        // After hydrating from localStorage, set isAuthenticated based on user
        if (state) {
          state.isAuthenticated = state.user !== null;
        }
      },
    }
  )
);
