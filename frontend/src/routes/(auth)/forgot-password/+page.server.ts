import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export const actions: Actions = {
    default: async ({ request, fetch }) => {
        const formData = await request.formData();
        const email = formData.get('email') as string;

        // Server-side validation
        if (!email) {
            return fail(400, {
                error: 'Please enter your email address',
                email
            });
        }

        // Basic email format validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            return fail(400, {
                error: 'Please enter a valid email address',
                email
            });
        }

        try {
            // Call backend forgot-password endpoint
            const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email }),
            });

            const data = await response.json();

            // Backend always returns success to prevent email enumeration
            // So we always show success to the user
            return {
                success: true,
                message: data.message || 'If an account with that email exists, a password reset link has been sent.'
            };

        } catch (error) {
            console.error('Forgot password error:', error);
            return fail(500, {
                error: 'Something went wrong. Please try again later.',
                email
            });
        }
    }
};
