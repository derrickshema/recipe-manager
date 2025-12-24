import type {
    AuthUser,
    LoginRequest,
    LoginResponse,
    RegisterCustomerRequest,
    RegisterRestaurantOwnerRequest,
    RegisterResponse,
    UpdateProfileRequest,
    ChangePasswordRequest,
    SuccessResponse
} from '$lib/types';
import { api } from '$lib/utils/apiHelpers';

/**
 * Authentication API Client
 * Handles all authentication-related HTTP requests
 */
export const authApi = {
    /**
     * Login user with credentials
     * @param credentials - Username and password
     * @returns Access token and token type
     */
    login: async (credentials: LoginRequest): Promise<LoginResponse> => {
        return api.post<LoginResponse>('/auth/token', credentials, { auth: false });
    },

    /**
     * Register new customer user
     * @param userData - Customer registration data
     * @returns Created user profile
     */
    register: async (userData: RegisterCustomerRequest): Promise<RegisterResponse> => {
        return api.post<RegisterResponse>('/auth/register', userData, { auth: false });
    },

    /**
     * Register restaurant owner with restaurant details
     * Creates user, restaurant, and membership atomically
     * @param registrationData - Owner and restaurant information
     * @returns Created user profile
     */
    registerRestaurantOwner: async (registrationData: RegisterRestaurantOwnerRequest): Promise<RegisterResponse> => {
        return api.post<RegisterResponse>('/auth/register/restaurant-owner', registrationData, { auth: false });
    },

    /**
     * Get current user profile
     * Requires authentication
     * @returns Current user profile
     */
    getProfile: async (): Promise<AuthUser> => {
        return api.get<AuthUser>('/auth/me');
    },

    /**
     * Update user profile
     * @param updates - Profile fields to update
     * @returns Updated user profile
     */
    updateProfile: async (updates: UpdateProfileRequest): Promise<AuthUser> => {
        return api.put<AuthUser>('/auth/me', updates);
    },

    /**
     * Change user password
     * @param oldPassword - Current password
     * @param newPassword - New password
     * @returns Success response
     */
    changePassword: async (oldPassword: string, newPassword: string): Promise<SuccessResponse> => {
        return api.post<SuccessResponse>(
            '/auth/change-password',
            { old_password: oldPassword, new_password: newPassword } as ChangePasswordRequest
        );
    }
};