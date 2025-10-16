import { writable, type Writable, get } from 'svelte/store';
import { browser } from '$app/environment';
import type { AuthUser } from '$lib/types/auth';

interface AuthStore extends Writable<AuthUser | null> {
    signIn: (user: AuthUser) => void;
    signOut: () => void;
}

interface AuthenticatedStore extends Writable<boolean> {
    setTrue: () => void;
    setFalse: () => void;
}

function createAuthStore(): AuthStore {
    const { subscribe, set } = writable<AuthUser | null>(null);
    
    return {
        subscribe,
        set,
        update: (updater) => {
            const store = get({ subscribe });
            set(updater(store));
        },
        signIn: (user: AuthUser) => set(user),
        signOut: () => set(null)
    };
}

function createAuthenticatedStore(): AuthenticatedStore {
    const { subscribe, set } = writable<boolean>(false);
    
    return {
        subscribe,
        set,
        update: (updater) => {
            const store = get({ subscribe });
            set(updater(store));
        },
        setTrue: () => set(true),
        setFalse: () => set(false)
    };
}

// Export the stores
export const user = createAuthStore();
export const isAuthenticated = createAuthenticatedStore();

// Initialize state from cookie if available
if (browser) {
    const checkAuth = async () => {
        try {
            const response = await fetch('/api/auth/me');
            if (response.ok) {
                const userData = await response.json();
                user.signIn(userData);
                isAuthenticated.setTrue();
            } else {
                user.signOut();
                isAuthenticated.setFalse();
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
            user.signOut();
            isAuthenticated.setFalse();
        }
    };

    checkAuth();
}