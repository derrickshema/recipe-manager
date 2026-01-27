import { fail, redirect } from '@sveltejs/kit';
import type { Actions, ServerLoad } from '@sveltejs/kit';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

// Redirect authenticated users away from registration
export const load: ServerLoad = async ({ cookies }) => {
    const token = cookies.get('access_token');
    if (token) {
        throw redirect(303, '/');
    }
    return {};
};

export const actions: Actions = {
    default: async ({ request, cookies, fetch }) => {
        const formData = await request.formData();
        const firstName = formData.get('firstName') as string;
        const lastName = formData.get('lastName') as string;
        const username = formData.get('username') as string;
        const email = formData.get('email') as string;
        const password = formData.get('password') as string;
        const confirmPassword = formData.get('confirmPassword') as string;

        // Server-side validation
        if (!firstName || !lastName || !username || !email || !password || !confirmPassword) {
            return fail(400, {
                error: 'Please fill in all fields',
                firstName,
                lastName,
                username,
                email
            });
        }

        if (password !== confirmPassword) {
            return fail(400, {
                error: 'Passwords do not match',
                firstName,
                lastName,
                username,
                email
            });
        }

        try {
            // Step 1: Register the user
            const registerResponse = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    username,
                    email,
                    password
                }),
            });

            if (!registerResponse.ok) {
                const errorData = await registerResponse.json().catch(() => ({}));
                return fail(registerResponse.status, {
                    error: errorData.detail || 'Registration failed',
                    firstName,
                    lastName,
                    username,
                    email
                });
            }

            // Registration successful - redirect to verify email page
            // Don't auto-login, require email verification first
            throw redirect(303, `/verify-email?registered=true&email=${encodeURIComponent(email)}`);
        } catch (err) {
            if (err instanceof Response || (err as any)?.status === 303) {
                throw err; // Re-throw redirects
            }
            console.error('Registration error:', err);
            return fail(500, {
                error: 'An unexpected error occurred. Please try again.',
                firstName,
                lastName,
                username,
                email
            });
        }
    }
};
