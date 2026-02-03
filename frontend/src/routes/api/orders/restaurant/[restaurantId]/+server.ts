import { json, type RequestHandler } from '@sveltejs/kit';
import { serverApi } from '$lib/server/api';
import type { Order } from '$lib/types';

// Get orders for a restaurant
export const GET: RequestHandler = async ({ params, url, cookies }) => {
	const { restaurantId } = params;
	const statusFilter = url.searchParams.get('status');
	
	let path = `/orders/restaurant/${restaurantId}`;
	if (statusFilter) {
		path += `?status_filter=${statusFilter}`;
	}
	
	try {
		const orders = await serverApi.get<Order[]>(path, cookies);
		return json(orders);
	} catch (err) {
		throw err;
	}
};
