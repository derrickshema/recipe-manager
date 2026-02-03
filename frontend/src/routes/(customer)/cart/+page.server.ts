/**
 * Cart page server load.
 * Just passes through user data - cart state is client-side only.
 */
export const load = async ({ parent }: { parent: () => Promise<{ user: unknown }> }) => {
    const { user } = await parent();
    
    return {
        user
    };
};
