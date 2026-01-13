import { redirect, type Handle } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';

/**
 * Routes that require authentication.
 * These are checked at the hook level for early redirect.
 * More granular role-based access is handled in layout server loads.
 */
const PROTECTED_ROUTES = [
    '/dashboard',
    '/recipes',
    '/staff',
    '/settings',
    '/overview',      // System admin
    '/restaurants',   // System admin
    '/home',          // Customer
];

/**
 * Routes that should only be accessible to unauthenticated users.
 */
const GUEST_ONLY_ROUTES = [
    '/login',
    '/register',
];

/**
 * Cookie name for the httpOnly auth token
 */
const AUTH_COOKIE_NAME = 'access_token';

/**
 * Authentication guard hook.
 * Handles basic auth redirects at the edge before page load.
 */
const authGuard: Handle = async ({ event, resolve }) => {
    const token = event.cookies.get(AUTH_COOKIE_NAME);
    const path = event.url.pathname;

    // Check if route requires authentication
    const isProtectedRoute = PROTECTED_ROUTES.some(route => path.startsWith(route));
    const isGuestOnlyRoute = GUEST_ONLY_ROUTES.some(route => path.startsWith(route));

    if (isProtectedRoute && !token) {
        // Redirect to login if trying to access protected route without auth
        const redirectUrl = encodeURIComponent(path);
        throw redirect(303, `/login?redirect=${redirectUrl}`);
    }

    if (isGuestOnlyRoute && token) {
        // Redirect authenticated users away from login/register pages
        // They'll be redirected to their appropriate dashboard by the page
        throw redirect(303, '/');
    }

    // Continue with the request
    const response = await resolve(event);
    return response;
};

// Export the sequence of hooks
export const handle = sequence(authGuard);