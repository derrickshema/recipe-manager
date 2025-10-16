import { apiFetch, type RequestConfig } from "./apiClient";

// Helper methods for common HTTP methods
export const api = {
    // GET: Path and optional config (Omit 'data' as GET requests have no body)
    get: async <T>(path: string, config?: Omit<RequestConfig, 'data'>) => {
        const response = await apiFetch(path, 'GET', config);
        // Add check for empty response body (e.g., 204 No Content)
        if (response.status === 204) return null as T; 
        return response.json() as Promise<T>;
    },

    // POST: Path, optional data (body payload), and optional config
    post: async <T>(path: string, data?: unknown, config?: RequestConfig<typeof data>) => {
        const response = await apiFetch(path, 'POST', { ...config, data });
        // Add check for empty response body (e.g., 201 Created with no body)
        if (response.status === 204) return null as T;
        return response.json() as Promise<T>;
    },

    // PUT: Path, optional data (body payload), and optional config
    put: async <T>(path: string, data?: unknown, config?: RequestConfig<typeof data>) => {
        const response = await apiFetch(path, 'PUT', { ...config, data });
        if (response.status === 204) return null as T;
        return response.json() as Promise<T>;
    },

    // PATCH: Path, optional data (body payload), and optional config
    patch: async <T>(path: string, data?: unknown, config?: RequestConfig<typeof data>) => {
        const response = await apiFetch(path, 'PATCH', { ...config, data });
        if (response.status === 204) return null as T;
        return response.json() as Promise<T>;
    },

    // DELETE: Path and optional config (Omit 'data' as DELETE requests have no body)
    delete: async <T>(path: string, config?: Omit<RequestConfig, 'data'>) => {
        const response = await apiFetch(path, 'DELETE', config);
        if (response.status === 204) return null as T;
        return response.json() as Promise<T>;
    },
} as const;