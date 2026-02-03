import { json, type RequestHandler } from '@sveltejs/kit';
import { serverApi } from '$lib/server/api';
import type { Order, OrderUpdateRequest } from '$lib/types';

// Update order status
export const PUT: RequestHandler = async ({ params, request, cookies }) => {
	const { orderId } = params;
	const updateData = await request.json();
	
	try {
		const order = await serverApi.put<Order>(`/orders/${orderId}/status`, updateData, cookies);
		return json(order);
	} catch (err) {
		throw err;
	}
};
