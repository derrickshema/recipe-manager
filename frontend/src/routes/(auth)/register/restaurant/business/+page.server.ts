import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
const REGISTRATION_COOKIE = 'registration_step1';

// Decode step 1 data from cookie
function decodeData(encoded: string): Record<string, string> | null {
    try {
        return JSON.parse(Buffer.from(encoded, 'base64').toString());
    } catch {
        return null;
    }
}

// Check for step 1 data and redirect if missing
export const load: PageServerLoad = async ({ cookies }) => {
    const token = cookies.get('access_token');
    if (token) {
        throw redirect(303, '/');
    }

    // Check if step 1 data exists
    const step1Cookie = cookies.get(REGISTRATION_COOKIE);
    if (!step1Cookie) {
        // User didn't complete step 1, redirect back
        throw redirect(303, '/register/restaurant');
    }

    const step1Data = decodeData(step1Cookie);
    if (!step1Data || !step1Data.email) {
        throw redirect(303, '/register/restaurant');
    }

    // Return only safe data to display (not password)
    return {
        ownerEmail: step1Data.email,
        ownerName: `${step1Data.firstName} ${step1Data.lastName}`
    };
};

export const actions: Actions = {
    default: async ({ request, cookies }) => {
        const formData = await request.formData();
        
        // Get step 1 data from cookie
        const step1Cookie = cookies.get(REGISTRATION_COOKIE);
        if (!step1Cookie) {
            return fail(400, {
                error: 'Session expired. Please start from step 1.',
            });
        }

        const step1Data = decodeData(step1Cookie);
        if (!step1Data) {
            cookies.delete(REGISTRATION_COOKIE, { path: '/' });
            return fail(400, {
                error: 'Invalid session. Please start from step 1.',
            });
        }

        // Owner info from cookie
        const { firstName, lastName, username, email, password, phoneNumber } = step1Data;
        
        // Restaurant info from form
        const restaurantName = formData.get('restaurantName') as string;
        const cuisineType = formData.get('cuisineType') as string;
        const address = formData.get('address') as string;
        const restaurantPhone = formData.get('restaurantPhone') as string;

        // Server-side validation
        if (!firstName || !lastName || !username || !email || !password) {
            return fail(400, {
                error: 'Owner information is incomplete. Please start from step 1.',
                restaurantName,
                cuisineType,
                address,
                restaurantPhone
            });
        }

        if (!restaurantName) {
            return fail(400, {
                error: 'Restaurant name is required',
                restaurantName,
                cuisineType,
                address,
                restaurantPhone
            });
        }

        try {
            // Step 1: Register restaurant owner
            const registerResponse = await fetch(`${API_BASE_URL}/auth/register/restaurant-owner`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    username,
                    email,
                    password,
                    phone_number: phoneNumber || undefined,
                    restaurant_name: restaurantName,
                    cuisine_type: cuisineType || undefined,
                    address: address || undefined,
                    restaurant_phone: restaurantPhone || undefined
                }),
            });

            if (!registerResponse.ok) {
                const errorData = await registerResponse.json().catch(() => ({}));
                return fail(registerResponse.status, {
                    error: errorData.detail || 'Registration failed',
                    restaurantName,
                    cuisineType,
                    address,
                    restaurantPhone
                });
            }

            // Step 2: Auto-login after successful registration
            const loginResponse = await fetch(`${API_BASE_URL}/auth/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            if (!loginResponse.ok) {
                throw redirect(303, '/login?registered=true');
            }

            const userData = await loginResponse.json();

            // Extract and set the httpOnly cookie
            const setCookieHeader = loginResponse.headers.get('set-cookie');
            if (setCookieHeader) {
                const tokenMatch = setCookieHeader.match(/access_token=([^;]+)/);
                if (tokenMatch) {
                    cookies.set('access_token', tokenMatch[1], {
                        path: '/',
                        httpOnly: true,
                        secure: process.env.NODE_ENV === 'production',
                        sameSite: 'lax',
                        maxAge: 60 * 60 * 24 * 7
                    });
                }
            }

            // Clean up the registration cookie
            cookies.delete(REGISTRATION_COOKIE, { path: '/' });

            return {
                success: true,
                user: userData
            };
        } catch (err) {
            if (err instanceof Response || (err as any)?.status === 303) {
                throw err;
            }
            console.error('Registration error:', err);
            return fail(500, {
                error: 'An unexpected error occurred. Please try again.',
                restaurantName,
                cuisineType,
                address,
                restaurantPhone
            });
        }
    }
};
