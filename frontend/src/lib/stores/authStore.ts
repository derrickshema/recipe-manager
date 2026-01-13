import { writable, derived } from 'svelte/store';
import type { AuthUser } from '$lib/types';

/**
 * Authentication Store
 * 
 * This store manages client-side auth state. With httpOnly cookies:
 * - Token is stored in httpOnly cookie (managed by server)
 * - User data is fetched via SSR and hydrated into this store
 * - Client-side JS never sees the actual token
 * 
 * Authentication Flow:
 * 1. User logs in via form action (server-side)
 * 2. Server sets httpOnly cookie
 * 3. Root layout server load fetches user profile
 * 4. Layout hydrates this store with user data
 */

// --- State Definition ---
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

// --- Store Creation ---
function createAuthStore() {
    const { subscribe, set, update } = writable<AuthState>(initialState);

    return {
        subscribe,
        set,
        update,

        /**
         * Set user data directly (used after SSR form action login or layout hydration)
         * The token is in httpOnly cookie, we just need the user data for UI
         */
        setUser(userData: AuthUser | null) {
            if (userData) {
                set({
                    user: {
                        ...userData,
                        isAuthenticated: true
                    },
                    isAuthenticated: true,
                    loading: false,
                    error: null
                });
            } else {
                set(initialState);
            }
        },

        /**
         * Set loading state
         */
        setLoading(loading: boolean) {
            update(state => ({ ...state, loading }));
        },

        /**
         * Set error state
         */
        setError(error: string | null) {
            update(state => ({ ...state, error, loading: false }));
        },

        /**
         * Reset store to initial state (used on logout)
         */
        reset() {
            set(initialState);
        }
    };
}

// Create the store instance
export const authStore = createAuthStore();

// Export derived stores for convenience
export const user = derived(authStore, $store => $store.user);
export const loading = derived(authStore, $store => $store.loading);
export const error = derived(authStore, $store => $store.error);
export const isAuthenticated = derived(authStore, $store => $store.isAuthenticated);
