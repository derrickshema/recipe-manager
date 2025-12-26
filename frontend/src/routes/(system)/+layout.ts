import { redirect } from '@sveltejs/kit';
import type { LayoutLoad } from './$types';
import { browser } from '$app/environment';
import { get } from 'svelte/store';
import { user } from '$lib/stores/authStore';
import { SystemRole } from '$lib/types/roles';

export const load: LayoutLoad = async () => {
    // Client-side authentication check
    if (browser) {
        const token = localStorage.getItem('access_token');
        const currentUser = get(user);
        
        // Check if token exists
        if (!token) {
            throw redirect(303, '/login');
        }
        
        // Check if user is authenticated and is a SUPERADMIN
        if (!currentUser || !currentUser.isAuthenticated || currentUser.role !== SystemRole.SUPERADMIN) {
            throw redirect(303, '/login');
        }
    }

    return {};
};