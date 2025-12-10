import type { Writable } from 'svelte/store';

interface StoreWithLoadingAndError {
    loading: boolean;
    error: string | null;
}

/**
 * Executes an async function while managing loading and error states in a store.
 * @param store The writable store instance
 * @param fn The async function to execute
 * @param errorMsg Default error message if the error is not an Error instance
 * @returns The result of the async function or null if it fails
 */
export async function handleAsyncStore<T, S extends StoreWithLoadingAndError>(
    store: Writable<S>,
    fn: () => Promise<T>,
    errorMsg: string = 'Operation failed'
): Promise<T | null> {
    store.update(state => ({ ...state, loading: true, error: null }));
    try {
        const result = await fn();
        store.update(state => ({ ...state, loading: false }));
        return result;
    } catch (error) {
        store.update(state => ({
            ...state,
            error: error instanceof Error ? error.message : errorMsg,
            loading: false
        }));
        return null;
    }
}

/**
 * Type guard to check if a caught error is an instance of Error
 */
export function isError(error: unknown): error is Error {
    return error instanceof Error;
}