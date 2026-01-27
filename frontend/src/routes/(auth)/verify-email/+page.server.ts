import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

// Load function to auto-verify if token is in URL
export const load: PageServerLoad = async ({ url, fetch }) => {
    const token = url.searchParams.get('token');
    const justRegistered = url.searchParams.get('registered') === 'true';
    const registeredEmail = url.searchParams.get('email');
    
    // If no token, show the page (user just registered or needs to resend)
    if (!token) {
        return { 
            autoVerified: false,
            error: null,
            message: null,
            justRegistered,
            registeredEmail
        };
    }
    
    // Auto-verify the token
    try {
        const response = await fetch(`${API_BASE_URL}/auth/verify-email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token }),
        });

        const data = await response.json();

        if (!response.ok) {
            return {
                autoVerified: false,
                error: data.detail || 'Verification failed. The link may have expired.',
                message: null,
                justRegistered: false,
                registeredEmail: null
            };
        }

        return {
            autoVerified: true,
            error: null,
            message: data.message,
            justRegistered: false,
            registeredEmail: null
        };
    } catch (error) {
        console.error('Email verification error:', error);
        return {
            autoVerified: false,
            error: 'An unexpected error occurred. Please try again.',
            message: null,
            justRegistered: false,
            registeredEmail: null
        };
    }
};

// Form action for resending verification email
export const actions: Actions = {
    resend: async ({ request, fetch }) => {
        const formData = await request.formData();
        const email = formData.get('email') as string;

        if (!email) {
            return fail(400, {
                error: 'Please enter your email address'
            });
        }

        // Basic email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            return fail(400, {
                error: 'Please enter a valid email address'
            });
        }

        try {
            const response = await fetch(`${API_BASE_URL}/auth/resend-verification`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email }),
            });

            const data = await response.json();

            if (!response.ok) {
                return fail(response.status, {
                    error: data.detail || 'Failed to resend verification email.'
                });
            }

            return {
                success: true,
                message: data.message
            };
        } catch (error) {
            console.error('Resend verification error:', error);
            return fail(500, {
                error: 'An unexpected error occurred. Please try again.'
            });
        }
    }
};
