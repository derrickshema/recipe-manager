import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

const REGISTRATION_COOKIE = 'registration_step1';

// Simple encoding for the cookie (in production, use proper encryption)
function encodeData(data: Record<string, string>): string {
    return Buffer.from(JSON.stringify(data)).toString('base64');
}

// Redirect authenticated users away from registration
export const load: PageServerLoad = async ({ cookies }) => {
    const token = cookies.get('access_token');
    if (token) {
        throw redirect(303, '/');
    }
    
    // Check if returning from step 2 (to restore form data)
    const savedData = cookies.get(REGISTRATION_COOKIE);
    if (savedData) {
        try {
            const data = JSON.parse(Buffer.from(savedData, 'base64').toString());
            // Don't send password back to client
            const { password, ...safeData } = data;
            return { savedData: safeData };
        } catch {
            // Invalid cookie, ignore
        }
    }
    
    return { savedData: null };
};

export const actions: Actions = {
    next: async ({ request, cookies }) => {
        const formData = await request.formData();
        
        const firstName = formData.get('firstName') as string;
        const lastName = formData.get('lastName') as string;
        const username = formData.get('username') as string;
        const email = formData.get('email') as string;
        const password = formData.get('password') as string;
        const confirmPassword = formData.get('confirmPassword') as string;
        const phoneNumber = formData.get('phoneNumber') as string;

        // Server-side validation
        if (!firstName || !lastName || !username || !email || !password || !confirmPassword) {
            return fail(400, {
                error: 'Please fill in all required fields',
                firstName,
                lastName,
                username,
                email,
                phoneNumber
            });
        }

        if (password !== confirmPassword) {
            return fail(400, {
                error: 'Passwords do not match',
                firstName,
                lastName,
                username,
                email,
                phoneNumber
            });
        }

        if (password.length < 8) {
            return fail(400, {
                error: 'Password must be at least 8 characters',
                firstName,
                lastName,
                username,
                email,
                phoneNumber
            });
        }

        // Store step 1 data in encrypted httpOnly cookie
        const step1Data = {
            firstName,
            lastName,
            username,
            email,
            password,
            phoneNumber
        };

        cookies.set(REGISTRATION_COOKIE, encodeData(step1Data), {
            path: '/',
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'strict',
            maxAge: 60 * 30 // 30 minutes
        });

        throw redirect(303, '/register/restaurant/business');
    }
};
