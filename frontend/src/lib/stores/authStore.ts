import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import type {
    AuthUser,
    LoginRequest,
    RegisterCustomerRequest,
    RegisterRestaurantOwnerRequest
} from '$lib/types';
import { handleAsyncStore } from '$lib/utils/storeHelpers';
import { authService } from '$lib/services/authService';

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

        /**
         * Login user
         * Delegates business logic to authService, manages state here
         * @param credentials - Username and password
         */
        async login(credentials: LoginRequest) {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const userProfile = await authService.login(credentials);
                    
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

        /**
         * Register new customer user
         * Delegates business logic to authService, manages state here
         * @param data - Customer registration data
         */
        async register(data: RegisterCustomerRequest) {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const userProfile = await authService.register(data);
                    
                    update(state => ({
                        ...state,
                        user: userProfile,
                        isAuthenticated: true
                    }));
                    
                    return userProfile;
                },
                'Registration failed'
            );
        },

        /**
         * Register restaurant owner with restaurant details
         * Delegates business logic to authService, manages state here
         * @param data - Owner and restaurant information
         */
        async registerRestaurantOwner(data: RegisterRestaurantOwnerRequest) {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const userProfile = await authService.registerRestaurantOwner(data);
                    
                    update(state => ({
                        ...state,
                        user: userProfile,
                        isAuthenticated: true
                    }));
                    
                    return userProfile;
                },
                'Restaurant registration failed'
            );
        },

        /**
         * Sign out user
         * Delegates business logic to authService, manages state here
         */
        async signOut() {
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    await authService.signOut();
                    update(() => initialState);
                },
                'Logout failed'
            );
        },

        /**
         * Initialize auth state
         * Checks for existing token and fetches user profile if valid
         */
        async initialize() {
            if (!browser) return;
            
            return handleAsyncStore(
                { subscribe, set, update },
                async () => {
                    const profile = await authService.checkAuth();
                    
                    if (profile) {
                        update(state => ({
                            ...state,
                            user: profile,
                            isAuthenticated: true
                        }));
                        return profile;
                    } else {
                        update(() => initialState);
                        return null;
                    }
                }
            );
        },

        /**
         * Reset store to initial state
         */
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