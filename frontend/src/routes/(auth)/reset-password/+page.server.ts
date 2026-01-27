import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export const actions: Actions = {
    default: async ({ request, fetch }) => {
        const formData = await request.formData();
        const token = formData.get('token') as string;
        const password = formData.get('password') as string;
        const confirmPassword = formData.get('confirmPassword') as string;

        // Server-side validation
        if (!token) {
            return fail(400, {
                error: 'Invalid reset link. Please request a new password reset.'
            });
        }

        if (!password || !confirmPassword) {
            return fail(400, {
                error: 'Please fill in all fields'
            });
        }

        if (password !== confirmPassword) {
            return fail(400, {
                error: 'Passwords do not match'
            });
        }

        if (password.length < 8) {
            return fail(400, {
                error: 'Password must be at least 8 characters long'
            });
        }

        try {
            // Call backend reset-password endpoint
            const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    token, 
                    new_password: password 
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                return fail(response.status, {
                    error: data.detail || 'Failed to reset password. The link may have expired.'
                });
            }

            return {
                success: true,
                message: data.message || 'Your password has been reset successfully.'
            };

        } catch (error) {
            console.error('Reset password error:', error);
            return fail(500, {
                error: 'Something went wrong. Please try again later.'
            });
        }
    }
};
