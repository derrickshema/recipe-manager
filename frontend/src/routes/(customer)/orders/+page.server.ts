import { serverApi } from '$lib/server/api';
import { redirect } from '@sveltejs/kit';
import type { Cookies } from '@sveltejs/kit';
import type { Order } from '$lib/types';

export const load = async ({ cookies, parent }: { cookies: Cookies; parent: () => Promise<{ user: { id: number } | null }> }) => {
	const { user } = await parent();
	
	try {
		const orders = await serverApi.get<Order[]>('/orders', cookies);
		return { orders, user };
	} catch (err: unknown) {
		// serverApi throws errors for non-2xx responses
		const error = err as { status?: number };
		if (error.status === 401) {
			throw redirect(302, '/login');
		}
		return { orders: [], error: 'Failed to load orders', user };
	}
};
