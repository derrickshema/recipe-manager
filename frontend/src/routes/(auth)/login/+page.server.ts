import { fail, redirect } from '@sveltejs/kit';
import type { Actions, ServerLoad } from '@sveltejs/kit';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

// Redirect authenticated users away from login page
export const load: ServerLoad = async ({ cookies }) => {
    const token = cookies.get('access_token');
    if (token) {
        // User is already logged in, redirect to home
        // The actual destination will be determined by user role on the client
        throw redirect(303, '/');
    }
    return {};
};

export const actions: Actions = {
    default: async ({ request, cookies, fetch }) => {
        const formData = await request.formData();
        const username = formData.get('username') as string;
        const password = formData.get('password') as string;

        // Server-side validation
        if (!username || !password) {
            return fail(400, {
                error: 'Please fill in all fields',
                username
            });
        }

        try {
            // Call backend login endpoint
            const response = await fetch(`${API_BASE_URL}/auth/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                
                if (response.status === 401) {
                    return fail(401, {
                        error: 'Invalid username or password',
                        username
                    });
                }
                
                return fail(response.status, {
                    error: errorData.detail || 'Login failed',
                    username
                });
            }

            // Get user data from response
            const userData = await response.json();

            // Extract the httpOnly cookie from backend response and set it on the client
            const setCookieHeader = response.headers.get('set-cookie');
            if (setCookieHeader) {
                // Parse the cookie from the backend and set it
                // The backend sets: access_token=...; HttpOnly; Secure; SameSite=Lax; Path=/
                const tokenMatch = setCookieHeader.match(/access_token=([^;]+)/);
                if (tokenMatch) {
                    cookies.set('access_token', tokenMatch[1], {
                        path: '/',
                        httpOnly: true,
                        secure: process.env.NODE_ENV === 'production',
                        sameSite: 'lax',
                        maxAge: 60 * 60 * 24 * 7 // 7 days
                    });
                }
            }

            // Return success with user data for client-side redirect handling
            return {
                success: true,
                user: userData
            };
        } catch (err) {
            console.error('Login error:', err);
            return fail(500, {
                error: 'An unexpected error occurred. Please try again.',
                username
            });
        }
    }
};
