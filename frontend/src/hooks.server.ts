import { redirect, type Handle } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';

// Protected routes configuration
const PROTECTED_ROUTES = [
    '/dashboard',
    '/profile',
    '/recipes',
    // Add other protected routes here
];

const GUEST_ROUTES = [
    '/login',
    '/register',
    // Add other guest-only routes here
];

// Authentication guard
const authGuard: Handle = async ({ event, resolve }) => {
    const token = event.cookies.get('token');
    const path = event.url.pathname;

    // Check if route requires authentication
    const isProtectedRoute = PROTECTED_ROUTES.some(route => path.startsWith(route));
    const isGuestRoute = GUEST_ROUTES.some(route => path.startsWith(route));

    if (isProtectedRoute && !token) {
        // Redirect to login if trying to access protected route without auth
        throw redirect(303, `/login?redirect=${path}`);
    }

    if (isGuestRoute && token) {
        // Redirect to dashboard if trying to access guest route while authenticated
        throw redirect(303, '/dashboard');
    }

    // Continue with the request
    const response = await resolve(event);
    return response;
};

// Export the sequence of hooks
export const handle = sequence(authGuard);