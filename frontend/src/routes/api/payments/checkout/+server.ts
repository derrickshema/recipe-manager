import { json, type RequestHandler } from '@sveltejs/kit';
import { serverApi } from '$lib/server/api';

/**
 * Create a Stripe Checkout Session for an order.
 * 
 * This proxies the request to our backend, which then talks to Stripe.
 * The response includes a checkout_url that we redirect the customer to.
 */
export const POST: RequestHandler = async ({ request, cookies }) => {
	const { order_id } = await request.json();
	
	try {
		const result = await serverApi.post<{ checkout_url: string; session_id: string }>(
			`/payments/create-checkout-session?order_id=${order_id}`,
			{},
			cookies
		);
		return json(result);
	} catch (err) {
		throw err;
	}
};
