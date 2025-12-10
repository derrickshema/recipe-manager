import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import type { AuthUser } from '$lib/types/auth';
import { authApi } from '$lib/api/auth';
import { handleAsyncStore } from '$lib/utils/storeHelpers';

// --- 1. State Definition ---
interface AuthState {
    user: AuthUser | null;
    loading: boolean;
    error: string | null;
    isAuthenticated: boolean;
}

const initialState: AuthState = {
    user: null,
    loading: false,
    error: null,
    isAuthenticated: false
};

// --- 2. Store Creation ---
function createAuthStore() {
    const { subscribe, set, update } = writable<AuthState>(initialState);

    const store = {
        subscribe,
        set,
        update,

        // Login user - OAuth2 flow
        async login(credentials: { username: string; password: string }) {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    // Step 1: Exchange credentials for access token
                    const tokenResponse = await authApi.login(credentials);
                    
                    // Step 2: Store token for future requests
                    if (browser && tokenResponse.access_token) {
                        localStorage.setItem('access_token', tokenResponse.access_token);
                    }
                    
                    // Step 3: Fetch user profile using the token
                    // (The token is automatically attached by apiClient now)
                    const userProfile = await authApi.getProfile();
                    
                    // Step 4: Update store with user data
                    update(state => ({
                        ...state,
                        user: userProfile,
                        isAuthenticated: true
                    }));
                    
                    return userProfile;
                },
                'Login failed'
            );
        },

        // Register new user
        async register(data: { email: string; password: string; username: string; first_name: string; last_name: string }) {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    await authApi.register(data);
                    return store.login({
                        username: data.username,
                        password: data.password
                    });
                },
                'Registration failed'
            );
        },

        // Sign out user
        async signOut() {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    // Clear stored token
                    if (browser) {
                        localStorage.removeItem('access_token');
                    }
                    
                    // Reset auth state
                    update(() => initialState);
                },
                'Logout failed'
            );
        },

        // Initialize auth state
        async initialize() {
            if (!browser) return;
            
            // Check if we have a stored token
            const token = localStorage.getItem('access_token');
            if (!token) {
                // No token, user is not logged in
                update(() => initialState);
                return;
            }
            
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    try {
                        // Try to fetch user profile with existing token
                        const profile = await authApi.getProfile();
                        update(state => ({
                            ...state,
                            user: profile,
                            isAuthenticated: true
                        }));
                        return profile;
                    } catch (error) {
                        // Token is invalid or expired, clear it
                        localStorage.removeItem('access_token');
                        update(() => initialState);
                        return null;
                    }
                }
            );
        },

        // Reset store to initial state
        reset() {
            set(initialState);
        }
    };

    // Initialize auth state when in browser
    if (browser) {
        store.initialize();
    }

    return store;
}

// Create the store instance
export const authStore = createAuthStore();

// Export derived stores for convenience
export const user = derived(authStore, $store => $store.user);
export const loading = derived(authStore, $store => $store.loading);
export const error = derived(authStore, $store => $store.error);
export const isAuthenticated = derived(authStore, $store => $store.isAuthenticated);