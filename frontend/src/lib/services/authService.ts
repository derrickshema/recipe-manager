import { browser } from '$app/environment';
import type {
    AuthUser,
    LoginRequest,
    RegisterCustomerRequest,
    RegisterRestaurantOwnerRequest
} from '$lib/types';
import { authApi } from '$lib/api/auth';

/**
 * Authentication Service
 * Handles business logic for authentication operations
 * Separated from state management for better testability and reusability
 */
export const authService = {
    /**
     * Login user with credentials
     * @param credentials - Username and password
     * @returns User profile after successful authentication
     */
    async login(credentials: LoginRequest): Promise<AuthUser> {
        // Step 1: Exchange credentials for access token
        const tokenResponse = await authApi.login(credentials);
        
        // Step 2: Store token for future requests
        if (browser && tokenResponse.access_token) {
            localStorage.setItem('access_token', tokenResponse.access_token);
        }
        
        // Step 3: Fetch user profile using the token
        const userProfile = await authApi.getProfile();
        
        // Transform response to add frontend-specific fields
        return {
            ...userProfile,
            isAuthenticated: true
        };
    },

    /**
     * Register new customer user and automatically log them in
     * @param data - Customer registration data
     * @returns User profile after successful registration
     */
    async register(data: RegisterCustomerRequest): Promise<AuthUser> {
        // Register the user
        await authApi.register(data);
        
        // Auto-login after registration
        return this.login({
            username: data.username,
            password: data.password
        });
    },

    /**
     * Register restaurant owner with restaurant details
     * Creates user, restaurant, and membership in one transaction
     * @param data - Owner and restaurant information
     * @returns User profile after successful registration
     */
    async registerRestaurantOwner(data: RegisterRestaurantOwnerRequest): Promise<AuthUser> {
        // Register the restaurant owner
        await authApi.registerRestaurantOwner(data);
        
        // Auto-login after registration
        return this.login({
            username: data.username,
            password: data.password
        });
    },

    /**
     * Sign out user by clearing stored token
     */
    async signOut(): Promise<void> {
        if (browser) {
            localStorage.removeItem('access_token');
        }
    },

    /**
     * Check if user has a valid token and fetch their profile
     * Returns user profile if token is valid, null otherwise
     */
    async checkAuth(): Promise<AuthUser | null> {
        if (!browser) return null;
        
        const token = localStorage.getItem('access_token');
        if (!token) return null;
        
        try {
            // Try to fetch user profile with existing token
            const profile = await authApi.getProfile();
            
            // Transform response to add frontend-specific fields
            return {
                ...profile,
                isAuthenticated: true
            };
        } catch (error) {
            // Token is invalid or expired, clear it
            localStorage.removeItem('access_token');
            return null;
        }
    },

    /**
     * Get stored access token
     */
    getToken(): string | null {
        if (!browser) return null;
        return localStorage.getItem('access_token');
    },

    /**
     * Check if user is authenticated (has valid token)
     */
    hasToken(): boolean {
        return !!this.getToken();
    }
};
