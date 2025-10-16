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

export interface RecipeCreate {
    title: string;
    description?: string;
    ingredients: string[];
    instructions: string[];
    prep_time?: number;
    cook_time?: number;
    servings?: number;
}

export interface RecipeUpdate {
    title?: string;
    description?: string;
    ingredients?: string[];
    instructions?: string[];
    prep_time?: number;
    cook_time?: number;
    servings?: number;
}