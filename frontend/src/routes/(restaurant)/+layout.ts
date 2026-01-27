// This file passes through server data and can add client-specific data
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ data }) => {
    // Pass through server data (user, restaurant)
    return {
        ...data
    };
};