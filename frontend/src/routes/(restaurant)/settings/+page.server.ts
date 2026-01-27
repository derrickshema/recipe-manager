import { fail } from '@sveltejs/kit';
import { serverApi } from '$lib/server/api';
import type { PageServerLoad, Actions } from './$types';
import type { Restaurant } from '$lib/types';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

/**
 * Server-side load function for the restaurant settings page.
 * Fetches the user's restaurant details.
 */
export const load: PageServerLoad = async ({ cookies }) => {
    try {
        // Get the user's restaurants
        const restaurants = await serverApi.get<Restaurant[]>('/restaurants/my', cookies);
        const restaurant = restaurants.length > 0 ? restaurants[0] : null;
        
        return {
            restaurant
        };
    } catch (error) {
        console.error('Error loading settings:', error);
        return {
            restaurant: null,
            error: 'Failed to load restaurant settings'
        };
    }
};

/**
 * Form actions for restaurant settings.
 */
export const actions: Actions = {
    /**
     * Update restaurant details
     */
    update: async ({ request, cookies }) => {
        const formData = await request.formData();
        const restaurantId = formData.get('restaurantId');
        const restaurantName = formData.get('restaurantName');
        const cuisineType = formData.get('cuisineType');
        const address = formData.get('address');
        const phone = formData.get('phone');

        if (!restaurantId) {
            return fail(400, { 
                action: 'update',
                error: 'Restaurant ID is required' 
            });
        }

        if (!restaurantName) {
            return fail(400, { 
                action: 'update',
                error: 'Restaurant name is required',
                values: { restaurantName, cuisineType, address, phone }
            });
        }

        try {
            await serverApi.put<Restaurant>(
                `/restaurants/${restaurantId}`,
                {
                    restaurant_name: String(restaurantName),
                    cuisine_type: cuisineType ? String(cuisineType) : undefined,
                    address: address ? String(address) : undefined,
                    phone: phone ? String(phone) : undefined,
                },
                cookies
            );

            return { 
                action: 'update',
                success: true, 
                message: 'Settings updated successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'update',
                error: error.body?.message || 'Failed to update settings',
                values: { restaurantName, cuisineType, address, phone }
            });
        }
    },

    /**
     * Upload restaurant logo
     */
    uploadLogo: async ({ request, cookies }) => {
        const formData = await request.formData();
        const restaurantId = formData.get('restaurantId');
        const file = formData.get('logo') as File;

        if (!restaurantId) {
            return fail(400, { 
                action: 'uploadLogo',
                error: 'Restaurant ID is required' 
            });
        }

        if (!file || file.size === 0) {
            return fail(400, { 
                action: 'uploadLogo',
                error: 'Please select an image file' 
            });
        }

        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            return fail(400, { 
                action: 'uploadLogo',
                error: 'Invalid file type. Please use JPEG, PNG, GIF, or WebP.' 
            });
        }

        // Validate file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
            return fail(400, { 
                action: 'uploadLogo',
                error: 'File too large. Maximum size is 5MB.' 
            });
        }

        try {
            // Step 1: Upload file to S3
            const token = cookies.get('access_token');
            const uploadFormData = new FormData();
            uploadFormData.append('file', file);

            const uploadResponse = await fetch(`${API_BASE_URL}/upload/restaurant-logo`, {
                method: 'POST',
                headers: {
                    'Cookie': `access_token=${token}`
                },
                body: uploadFormData
            });

            if (!uploadResponse.ok) {
                const errorData = await uploadResponse.json().catch(() => ({}));
                return fail(uploadResponse.status, { 
                    action: 'uploadLogo',
                    error: errorData.detail || 'Failed to upload image' 
                });
            }

            const uploadData = await uploadResponse.json();
            const logoUrl = uploadData.url;

            // Step 2: Update restaurant with logo URL
            await serverApi.put<Restaurant>(
                `/restaurants/${restaurantId}`,
                { logo_url: logoUrl },
                cookies
            );

            return { 
                action: 'uploadLogo',
                success: true, 
                message: 'Logo uploaded successfully' 
            };
        } catch (error: any) {
            console.error('Logo upload error:', error);
            return fail(error.status || 500, { 
                action: 'uploadLogo',
                error: error.body?.message || 'Failed to upload logo' 
            });
        }
    },

    /**
     * Remove restaurant logo
     */
    removeLogo: async ({ request, cookies }) => {
        const formData = await request.formData();
        const restaurantId = formData.get('restaurantId');
        const logoUrl = formData.get('logoUrl');

        if (!restaurantId) {
            return fail(400, { 
                action: 'removeLogo',
                error: 'Restaurant ID is required' 
            });
        }

        try {
            // Step 1: Delete from S3 (if URL exists)
            if (logoUrl) {
                const token = cookies.get('access_token');
                await fetch(`${API_BASE_URL}/upload/restaurant-logo?file_url=${encodeURIComponent(String(logoUrl))}`, {
                    method: 'DELETE',
                    headers: {
                        'Cookie': `access_token=${token}`
                    }
                });
                // We don't fail if S3 delete fails - just clear the URL
            }

            // Step 2: Clear logo URL in database
            await serverApi.put<Restaurant>(
                `/restaurants/${restaurantId}`,
                { logo_url: null },
                cookies
            );

            return { 
                action: 'removeLogo',
                success: true, 
                message: 'Logo removed successfully' 
            };
        } catch (error: any) {
            return fail(error.status || 500, { 
                action: 'removeLogo',
                error: error.body?.message || 'Failed to remove logo' 
            });
        }
    }
};
