import { json, error, type RequestHandler } from '@sveltejs/kit';
import { serverApi } from '$lib/server/api';
import type { Order } from '$lib/types';

// Create a new order
export const POST: RequestHandler = async ({ request, cookies }) => {
	try {
		const orderData = await request.json();
		const order = await serverApi.post<Order>('/orders', orderData, cookies);
		return json(order);
	} catch (err) {
		// serverApi throws SvelteKit errors, re-throw them
		throw err;
	}
};

// Get customer's orders
export const GET: RequestHandler = async ({ cookies }) => {
	try {
		const orders = await serverApi.get<Order[]>('/orders', cookies);
		return json(orders);
	} catch (err) {
		throw err;
	}
};
