import type { PageServerLoad } from './$types';
import { serverApi } from '$lib/server/api';
import { redirect } from '@sveltejs/kit';
import type { Order } from '$lib/types';

export const load: PageServerLoad = async ({ parent, cookies }) => {
	const { restaurant } = await parent();
	
	if (!restaurant) {
		throw redirect(302, '/dashboard');
	}
	
	try {
		const orders = await serverApi.get<Order[]>(`/orders/restaurant/${restaurant.id}`, cookies);
		return { orders, restaurant };
	} catch (err) {
		console.error('Failed to load orders:', err);
		return { orders: [], error: 'Failed to load orders', restaurant };
	}
};
