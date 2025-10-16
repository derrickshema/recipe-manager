export interface Restaurant {
    id: number;
    restaurant_name: string;
    created_at: string;
    updated_at: string;
}

export interface RestaurantCreate {
    restaurant_name: string;
}

export interface RestaurantUpdate {
    restaurant_name?: string;
}

// Membership related types
export enum OrgRole {
    RESTAURANT_ADMIN = "restaurant_admin",
    EMPLOYEE = "employee",
    VIEWER = "viewer"
}

export interface Membership {
    id: number;
    user_id: number;
    restaurant_id: number;
    role: OrgRole;
}