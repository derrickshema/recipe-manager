import type { AuthUser, LoginResponse, RegisterResponse } from '$lib/types/auth';
import { api } from '$lib/utils/apiHelpers';

export const authApi = {
    // Login user - sends JSON credentials
    login: async (credentials: { username: string; password: string }) => {
        return api.post<{ access_token: string; token_type: string }>('/auth/token', credentials, { auth: false });
    },

    // Register new user
    register: async (userData: unknown) => {
        return api.post<RegisterResponse>('/auth/register', userData, { auth: false });
    },

    // Get current user profile
    getProfile: async () => {
        return api.get<AuthUser>('/auth/me');
    },

    // Update user profile
    updateProfile: async (updates: Partial<Omit<AuthUser, 'id' | 'role'>>) => {
        return api.put<AuthUser>('/auth/me', updates);
    },

    // Change password
    changePassword: async (oldPassword: string, newPassword: string) => {
        return api.post<{ old_password: string; new_password: string }>(
            '/auth/change-password',
            { old_password: oldPassword, new_password: newPassword }
        );
    }
};