// This file is kept for potential client-side universal load data
// Authentication is now handled server-side in +layout.server.ts
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async () => {
    // Client-side load can add any client-specific data here
    return {};
};