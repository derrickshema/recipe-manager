import { writable } from 'svelte/store';

export interface RestaurantRegistrationData {
	// Step 1: Owner Information
	first_name: string;
	last_name: string;
	username: string;
	email: string;
	password: string;
	phone_number?: string;
	
	// Step 2: Restaurant Information
	restaurant_name: string;
	cuisine_type?: string;
	address?: string;
	restaurant_phone?: string;
}

const initialData: RestaurantRegistrationData = {
	first_name: '',
	last_name: '',
	username: '',
	email: '',
	password: '',
	phone_number: '',
	restaurant_name: '',
	cuisine_type: '',
	address: '',
	restaurant_phone: ''
};

function createRestaurantRegistrationStore() {
	const { subscribe, set, update } = writable<RestaurantRegistrationData>(initialData);

	return {
		subscribe,
		updateOwnerInfo: (data: Partial<RestaurantRegistrationData>) => {
			update(state => ({ ...state, ...data }));
		},
		updateRestaurantInfo: (data: Partial<RestaurantRegistrationData>) => {
			update(state => ({ ...state, ...data }));
		},
		reset: () => set(initialData),
		getData: (): Promise<RestaurantRegistrationData> => {
			return new Promise(resolve => {
				const unsubscribe = subscribe(data => {
					unsubscribe();
					resolve(data);
				});
			});
		}
	};
}

export const restaurantRegistrationStore = createRestaurantRegistrationStore();
