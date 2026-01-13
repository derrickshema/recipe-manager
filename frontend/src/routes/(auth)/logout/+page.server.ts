import { redirect } from '@sveltejs/kit';
import type { Actions } from '@sveltejs/kit';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export const actions: Actions = {
    default: async ({ cookies, fetch }) => {
        // Call backend logout to invalidate session (if needed)
        try {
            await fetch(`${API_BASE_URL}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Cookie': `access_token=${cookies.get('access_token')}`
                }
            });
        } catch {
            // Ignore backend errors - we'll clear the cookie anyway
        }

        // Clear the httpOnly cookie
        cookies.delete('access_token', { path: '/' });

        // Redirect to login page
        throw redirect(303, '/login');
    }
};
