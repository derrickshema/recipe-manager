/**
 * Cart Store
 * 
 * Manages the shopping cart state across the application.
 * Uses Svelte's writable store for reactive state management.
 * 
 * Key concepts:
 * - Writable store: Can be read and written to from any component
 * - Derived store: Computed values that update when dependencies change
 * - Persistence: Cart is saved to localStorage so it survives page refreshes
 */

import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import type { Recipe } from '$lib/types';

// ==================== Types ====================

export interface CartItem {
    recipe: Recipe;           // The menu item
    quantity: number;         // How many
    notes?: string;           // Special instructions
}

export interface Cart {
    restaurantId: number | null;   // Which restaurant (can only order from one at a time)
    restaurantName: string | null; // For display purposes
    items: CartItem[];             // Items in the cart
}

// ==================== Initial State ====================

const CART_STORAGE_KEY = 'recipe-manager-cart';

// Try to load cart from localStorage (only in browser)
function loadCartFromStorage(): Cart {
    if (browser) {
        const stored = localStorage.getItem(CART_STORAGE_KEY);
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch {
                // Invalid JSON, return default
            }
        }
    }
    return {
        restaurantId: null,
        restaurantName: null,
        items: []
    };
}

// ==================== Store Creation ====================

// Create the writable store with initial state
const cartStore = writable<Cart>(loadCartFromStorage());

// Save to localStorage whenever cart changes (only in browser)
if (browser) {
    cartStore.subscribe((cart) => {
        localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
    });
}

// ==================== Derived Stores ====================

// Total number of items in cart
export const cartItemCount = derived(cartStore, ($cart) => 
    $cart.items.reduce((total, item) => total + item.quantity, 0)
);

// Total price of cart
export const cartTotal = derived(cartStore, ($cart) =>
    $cart.items.reduce((total, item) => total + (item.recipe.price * item.quantity), 0)
);

// ==================== Cart Actions ====================

/**
 * Add an item to the cart.
 * If ordering from a different restaurant, clears the cart first.
 */
export function addToCart(recipe: Recipe, restaurantId: number, restaurantName: string, quantity: number = 1, notes?: string) {
    cartStore.update((cart) => {
        // If switching restaurants, clear the cart
        if (cart.restaurantId !== null && cart.restaurantId !== restaurantId) {
            // Could show a confirmation dialog here
            cart = {
                restaurantId,
                restaurantName,
                items: []
            };
        }
        
        // Set restaurant if cart is empty
        if (cart.restaurantId === null) {
            cart.restaurantId = restaurantId;
            cart.restaurantName = restaurantName;
        }
        
        // Check if item already exists in cart
        const existingIndex = cart.items.findIndex(item => item.recipe.id === recipe.id);
        
        if (existingIndex >= 0) {
            // Update quantity
            cart.items[existingIndex].quantity += quantity;
            if (notes) {
                cart.items[existingIndex].notes = notes;
            }
        } else {
            // Add new item
            cart.items.push({ recipe, quantity, notes });
        }
        
        return { ...cart };
    });
}

/**
 * Update the quantity of an item in the cart.
 */
export function updateCartItemQuantity(recipeId: number, quantity: number) {
    cartStore.update((cart) => {
        const index = cart.items.findIndex(item => item.recipe.id === recipeId);
        
        if (index >= 0) {
            if (quantity <= 0) {
                // Remove item if quantity is 0 or less
                cart.items.splice(index, 1);
            } else {
                cart.items[index].quantity = quantity;
            }
        }
        
        // If cart is empty, reset restaurant
        if (cart.items.length === 0) {
            cart.restaurantId = null;
            cart.restaurantName = null;
        }
        
        return { ...cart };
    });
}

/**
 * Remove an item from the cart.
 */
export function removeFromCart(recipeId: number) {
    updateCartItemQuantity(recipeId, 0);
}

/**
 * Clear the entire cart.
 */
export function clearCart() {
    cartStore.set({
        restaurantId: null,
        restaurantName: null,
        items: []
    });
}

/**
 * Update notes for an item.
 */
export function updateCartItemNotes(recipeId: number, notes: string) {
    cartStore.update((cart) => {
        const item = cart.items.find(item => item.recipe.id === recipeId);
        if (item) {
            item.notes = notes;
        }
        return { ...cart };
    });
}

// Export the store for reading
export const cart = {
    subscribe: cartStore.subscribe
};
