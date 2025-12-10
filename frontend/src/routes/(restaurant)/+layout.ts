import { redirect } from '@sveltejs/kit';
import type { LayoutLoad } from './$types';
import { browser } from '$app/environment';

export const load: LayoutLoad = async () => {
    // Client-side authentication check
    if (browser) {
        const token = localStorage.getItem('access_token');
        if (!token) {
            throw redirect(303, '/login');
        }
    }

    return {};
};