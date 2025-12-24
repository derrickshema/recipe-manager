// ==================== Core Recipe Types ====================

/**
 * Complete recipe entity
 * Returned from GET /recipes/{id}
 */
export interface Recipe {
    id: number;
    title: string;
    description?: string;
    ingredients: string[];
    instructions: string[];
    prep_time?: number;
    cook_time?: number;
    servings?: number;
    created_at: string;
    updated_at: string;
    restaurant_id: number;
}

// ==================== Recipe Operations ====================

/**
 * Recipe creation request payload
 * Sent to POST /recipes
 */
export interface RecipeCreateRequest {
    title: string;
    description?: string;
    ingredients: string[];
    instructions: string[];
    prep_time?: number;
    cook_time?: number;
    servings?: number;
}

/**
 * Recipe update request payload
 * Sent to PUT /recipes/{id}
 */
export interface RecipeUpdateRequest {
    title?: string;
    description?: string;
    ingredients?: string[];
    instructions?: string[];
    prep_time?: number;
    cook_time?: number;
    servings?: number;
}

/**
 * Response from recipe list endpoint
 * GET /recipes/?restaurant_id={id}
 */
export interface RecipeListResponse {
    recipes: Recipe[];
    total: number;
}

// Type aliases for backward compatibility
export type RecipeCreate = RecipeCreateRequest;
export type RecipeUpdate = RecipeUpdateRequest;