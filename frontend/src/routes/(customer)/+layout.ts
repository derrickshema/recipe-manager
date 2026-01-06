import { redirect } from '@sveltejs/kit';
import { get } from 'svelte/store';
import { isAuthenticated, user } from '$lib/stores/authStore';
import { SystemRole } from '$lib/types';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async () => {
	const authenticated = get(isAuthenticated);
	const currentUser = get(user);

	// Redirect to login if not authenticated
	if (!authenticated) {
		throw redirect(302, '/login');
	}

	// Ensure user is a customer
	if (currentUser?.role !== SystemRole.CUSTOMER) {
		throw redirect(302, '/');
	}

	return {};
};
