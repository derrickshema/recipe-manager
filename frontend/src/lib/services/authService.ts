/**
 * Authentication Service
 * 
 * NOTE: With the SSR httpOnly cookie architecture, most auth operations
 * are now handled via SvelteKit form actions and server load functions.
 * 
 * This service is kept minimal for any client-side auth utilities needed.
 * The actual token is in an httpOnly cookie and not accessible here.
 */

/**
 * Client-side auth utilities
 * Note: Actual authentication state comes from SSR-hydrated stores
 */
export const authService = {
    /**
     * Trigger logout by submitting to the logout form action
     * This clears the httpOnly cookie server-side
     */
    async signOut(): Promise<void> {
        // The logout is handled by form action at /logout
        // This is a fallback for programmatic logout
        const response = await fetch('/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });
        
        if (response.redirected) {
            window.location.href = response.url;
        }
    }
};
