import type { ServerLoad } from '@sveltejs/kit';

// API base URL - use environment variable in production
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

/**
 * Root layout server load function.
 * This runs on EVERY request and makes user data available to all pages.
 * The httpOnly cookie is automatically sent with SSR requests.
 */
export const load: ServerLoad = async ({ cookies, fetch }) => {
    const token = cookies.get('access_token');
    
    if (!token) {
        return {
            user: null
        };
    }
    
    try {
        // Fetch user profile from backend
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Cookie': `access_token=${token}`
            }
        });
        
        if (!response.ok) {
            // Token is invalid or expired - clear the cookie
            if (response.status === 401) {
                cookies.delete('access_token', { path: '/' });
            }
            return {
                user: null
            };
        }
        
        const user = await response.json();
        
        return {
            user: {
                ...user,
                isAuthenticated: true
            }
        };
    } catch (error) {
        console.error('Error fetching user profile:', error);
        return {
            user: null
        };
    }
};
