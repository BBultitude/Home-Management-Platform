import axios from 'axios';

// Get API URL from environment or default to /api/v1 for production
const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Send cookies with requests
});

// Request interceptor (no need to manually add token - it's in HTTP-only cookie)
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // Only redirect to login on 401 if NOT on login/auth endpoints
    if (error.response?.status === 401 && !error.config?.url?.includes('/auth/login')) {
      // Session expired - clear auth and redirect to login
      localStorage.removeItem('auth-storage');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);
