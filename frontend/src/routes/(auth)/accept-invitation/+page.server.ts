import { fail, redirect, type Actions, type ServerLoadEvent } from '@sveltejs/kit';
import { serverApi } from '$lib/server/api';

interface InvitationInfo {
    email: string;
    restaurant_id: number;
    restaurant_name: string;
    role: string;
    valid: boolean;
}

/**
 * Load function to verify the invitation token and get details.
 */
export const load = async ({ url, cookies }: ServerLoadEvent) => {
    const token = url.searchParams.get('token');
    
    if (!token) {
        return {
            invitation: null,
            error: 'No invitation token provided'
        };
    }
    
    try {
        // Verify the token (this endpoint doesn't require auth)
        const invitation = await serverApi.get<InvitationInfo>(
            `/restaurants/invitation/verify?token=${encodeURIComponent(token)}`,
            cookies
        );
        
        return {
            invitation,
            token,
            error: null
        };
    } catch (error: any) {
        console.error('Error verifying invitation:', error);
        return {
            invitation: null,
            token,
            error: error.body?.detail || 'Invalid or expired invitation'
        };
    }
};

/**
 * Action to accept the invitation.
 */
export const actions: Actions = {
    accept: async ({ request, cookies }: { request: Request; cookies: any }) => {
        const formData = await request.formData();
        const token = formData.get('token');
        
        if (!token) {
            return fail(400, { error: 'No invitation token provided' });
        }
        
        try {
            await serverApi.post(
                '/restaurants/invitation/accept',
                { token: String(token) },
                cookies
            );
            
            // Redirect to dashboard on success
            throw redirect(303, '/dashboard');
        } catch (error: any) {
            // Handle redirect
            if (error.status === 303) {
                throw error;
            }
            
            return fail(error.status || 500, {
                error: error.body?.detail || 'Failed to accept invitation'
            });
        }
    }
};
