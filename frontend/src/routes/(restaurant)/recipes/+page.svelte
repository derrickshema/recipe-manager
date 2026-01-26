<script lang="ts">
    import { enhance } from '$app/forms';
    import { Button } from '$lib/components';
    import Modal from '$lib/components/modals/Modal.svelte';
    import ImageUpload from '$lib/components/forms/ImageUpload.svelte';
    import type { Recipe } from '$lib/types';

    // SSR data from +page.server.ts
    let { data, form } = $props();

    // Reactive state
    let showCreateModal = $state(false);
    let showEditModal = $state(false);
    let editingRecipe = $state<Recipe | null>(null);
    let submitting = $state(false);

    // Derived from SSR data
    let restaurant = $derived(data.restaurant);
    let recipes = $derived(data.recipes ?? []);

    // Form values for create/edit (now includes imageUrl)
    let formValues = $state({
        title: '',
        description: '',
        ingredients: '',
        instructions: '',
        prepTime: '',
        cookTime: '',
        servings: '',
        imageUrl: ''
    });

    function openCreateModal() {
        console.log('openCreateModal called, showCreateModal:', showCreateModal);
        formValues = {
            title: '',
            description: '',
            ingredients: '',
            instructions: '',
            prepTime: '',
            cookTime: '',
            servings: '',
            imageUrl: ''
        };
        showCreateModal = true;
        console.log('showCreateModal after:', showCreateModal);
    }

    function openEditModal(recipe: Recipe) {
        editingRecipe = recipe;
        formValues = {
            title: recipe.title,
            description: recipe.description || '',
            ingredients: recipe.ingredients.join('\n'),
            instructions: recipe.instructions.join('\n'),
            prepTime: recipe.prep_time?.toString() || '',
            cookTime: recipe.cook_time?.toString() || '',
            servings: recipe.servings?.toString() || '',
            imageUrl: recipe.image_url || ''
        };
        showEditModal = true;
    }

    function closeModals() {
        showCreateModal = false;
        showEditModal = false;
        editingRecipe = null;
    }

    // Close modal on successful action
    $effect(() => {
        if (form?.success) {
            closeModals();
        }
    });
</script>

<div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
        <div>
            <a href="/dashboard" class="text-sm text-muted-foreground hover:text-foreground mb-2 inline-block">
                ← Back to Dashboard
            </a>
            <h1 class="text-3xl font-bold">Recipes</h1>
            {#if restaurant}
                <p class="text-muted-foreground mt-1">{restaurant.restaurant_name}</p>
            {/if}
        </div>
        <Button onclick={openCreateModal}>+ Add Recipe</Button>
    </div>

    <!-- Messages -->
    {#if form?.success}
        <div class="bg-green-100 text-green-800 p-4 rounded-lg">
            {form.message}
        </div>
    {/if}
    {#if form?.error}
        <div class="bg-destructive/10 text-destructive p-4 rounded-lg">
            {form.error}
        </div>
    {/if}
    {#if data.error}
        <div class="bg-destructive/10 text-destructive p-4 rounded-lg">
            {data.error}
        </div>
    {/if}

    <!-- Recipe List -->
    {#if recipes.length === 0}
        <div class="text-center py-12 bg-muted/30 rounded-lg">
            <p class="text-muted-foreground mb-4">No recipes yet</p>
            <Button onclick={openCreateModal}>Create your first recipe</Button>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each recipes as recipe (recipe.id)}
                <div class="bg-card border rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                    <!-- Recipe Image -->
                    {#if recipe.image_url}
                        <img 
                            src={recipe.image_url} 
                            alt={recipe.title}
                            class="w-full h-48 object-cover"
                        />
                    {:else}
                        <div class="w-full h-48 bg-muted/30 flex items-center justify-center">
                            <svg class="w-12 h-12 text-muted-foreground/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                        </div>
                    {/if}
                    
                    <div class="p-6">
                        <h3 class="text-xl font-semibold mb-2">{recipe.title}</h3>
                        {#if recipe.description}
                            <p class="text-muted-foreground text-sm mb-4 line-clamp-2">{recipe.description}</p>
                        {/if}
                    
                        <div class="flex gap-4 text-sm text-muted-foreground mb-4">
                            {#if recipe.prep_time}
                                <span>Prep: {recipe.prep_time}min</span>
                            {/if}
                            {#if recipe.cook_time}
                                <span>Cook: {recipe.cook_time}min</span>
                            {/if}
                            {#if recipe.servings}
                                <span>Serves: {recipe.servings}</span>
                            {/if}
                        </div>

                        <div class="flex gap-2">
                            <Button 
                                variant="secondary" 
                                size="sm"
                                onclick={() => openEditModal(recipe)}
                            >
                                Edit
                            </Button>
                            <form 
                                method="POST" 
                                action="?/delete"
                                use:enhance={() => {
                                    if (!confirm('Are you sure you want to delete this recipe?')) {
                                        return () => {};
                                    }
                                    submitting = true;
                                    return async ({ update }) => {
                                        await update();
                                        submitting = false;
                                    };
                                }}
                            >
                                <input type="hidden" name="recipeId" value={recipe.id} />
                                <input type="hidden" name="restaurantId" value={restaurant?.id} />
                                <Button 
                                    type="submit"
                                    variant="danger" 
                                    size="sm"
                                    disabled={submitting}
                                >
                                    Delete
                                </Button>
                            </form>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>

<!-- Create Recipe Modal -->
{#if showCreateModal}
    <Modal open={true} title="Create Recipe" onClose={closeModals}>
        <form 
            method="POST" 
            action="?/create"
            class="space-y-4"
            use:enhance={() => {
                submitting = true;
                return async ({ update }) => {
                    await update();
                    submitting = false;
                };
            }}
        >
            <input type="hidden" name="restaurantId" value={restaurant?.id} />
            
            <div>
                <label for="title" class="block text-sm font-medium mb-1">Title *</label>
                <input 
                    type="text" 
                    id="title" 
                    name="title" 
                    bind:value={formValues.title}
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                    required
                />
            </div>

            <div>
                <label for="description" class="block text-sm font-medium mb-1">Description</label>
                <textarea 
                    id="description" 
                    name="description" 
                    bind:value={formValues.description}
                    rows="2"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                ></textarea>
            </div>

            <!-- Image Upload -->
            <ImageUpload
                imageUrl={formValues.imageUrl}
                onUpload={(url) => formValues.imageUrl = url}
                onRemove={() => formValues.imageUrl = ''}
                disabled={submitting}
            />
            <input type="hidden" name="imageUrl" value={formValues.imageUrl} />

            <div class="grid grid-cols-3 gap-4">
                <div>
                    <label for="prepTime" class="block text-sm font-medium mb-1">Prep Time (min)</label>
                    <input 
                        type="number" 
                        id="prepTime" 
                        name="prepTime" 
                        bind:value={formValues.prepTime}
                        class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                    />
                </div>
                <div>
                    <label for="cookTime" class="block text-sm font-medium mb-1">Cook Time (min)</label>
                    <input 
                        type="number" 
                        id="cookTime" 
                        name="cookTime" 
                        bind:value={formValues.cookTime}
                        class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                    />
                </div>
                <div>
                    <label for="servings" class="block text-sm font-medium mb-1">Servings</label>
                    <input 
                        type="number" 
                        id="servings" 
                        name="servings" 
                        bind:value={formValues.servings}
                        class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                    />
                </div>
            </div>

            <div>
                <label for="ingredients" class="block text-sm font-medium mb-1">Ingredients (one per line)</label>
                <textarea 
                    id="ingredients" 
                    name="ingredients" 
                    bind:value={formValues.ingredients}
                    rows="4"
                    placeholder="1 cup flour&#10;2 eggs&#10;1/2 cup sugar"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                ></textarea>
            </div>

            <div>
                <label for="instructions" class="block text-sm font-medium mb-1">Instructions (one step per line)</label>
                <textarea 
                    id="instructions" 
                    name="instructions" 
                    bind:value={formValues.instructions}
                    rows="4"
                    placeholder="Preheat oven to 350°F&#10;Mix dry ingredients&#10;Add wet ingredients"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                ></textarea>
            </div>

            <div class="flex justify-end gap-2 pt-4">
                <Button type="button" variant="secondary" onclick={closeModals}>Cancel</Button>
                <Button type="submit" disabled={submitting}>
                    {submitting ? 'Creating...' : 'Create Recipe'}
                </Button>
            </div>
        </form>
    </Modal>
{/if}

<!-- Edit Recipe Modal -->
{#if showEditModal && editingRecipe}
    <Modal open={true} title="Edit Recipe" onClose={closeModals}>
        <form 
            method="POST" 
            action="?/update"
            class="space-y-4"
            use:enhance={() => {
                submitting = true;
                return async ({ update }) => {
                    await update();
                    submitting = false;
                };
            }}
        >
            <input type="hidden" name="recipeId" value={editingRecipe.id} />
            <input type="hidden" name="restaurantId" value={restaurant?.id} />
            
            <div>
                <label for="edit-title" class="block text-sm font-medium mb-1">Title *</label>
                <input 
                    type="text" 
                    id="edit-title" 
                    name="title" 
                    bind:value={formValues.title}
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                    required
                />
            </div>

            <div>
                <label for="edit-description" class="block text-sm font-medium mb-1">Description</label>
                <textarea 
                    id="edit-description" 
                    name="description" 
                    bind:value={formValues.description}
                    rows="2"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                ></textarea>
            </div>

            <!-- Image Upload -->
            <ImageUpload
                imageUrl={formValues.imageUrl}
                onUpload={(url) => formValues.imageUrl = url}
                onRemove={() => formValues.imageUrl = ''}
                disabled={submitting}
            />
            <input type="hidden" name="imageUrl" value={formValues.imageUrl} />

            <div class="grid grid-cols-3 gap-4">
                <div>
                    <label for="edit-prepTime" class="block text-sm font-medium mb-1">Prep Time (min)</label>
                    <input 
                        type="number" 
                        id="edit-prepTime" 
                        name="prepTime" 
                        bind:value={formValues.prepTime}
                        class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                    />
                </div>
                <div>
                    <label for="edit-cookTime" class="block text-sm font-medium mb-1">Cook Time (min)</label>
                    <input 
                        type="number" 
                        id="edit-cookTime" 
                        name="cookTime" 
                        bind:value={formValues.cookTime}
                        class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                    />
                </div>
                <div>
                    <label for="edit-servings" class="block text-sm font-medium mb-1">Servings</label>
                    <input 
                        type="number" 
                        id="edit-servings" 
                        name="servings" 
                        bind:value={formValues.servings}
                        class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                    />
                </div>
            </div>

            <div>
                <label for="edit-ingredients" class="block text-sm font-medium mb-1">Ingredients (one per line)</label>
                <textarea 
                    id="edit-ingredients" 
                    name="ingredients" 
                    bind:value={formValues.ingredients}
                    rows="4"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                ></textarea>
            </div>

            <div>
                <label for="edit-instructions" class="block text-sm font-medium mb-1">Instructions (one step per line)</label>
                <textarea 
                    id="edit-instructions" 
                    name="instructions" 
                    bind:value={formValues.instructions}
                    rows="4"
                    class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                ></textarea>
            </div>

            <div class="flex justify-end gap-2 pt-4">
                <Button type="button" variant="secondary" onclick={closeModals}>Cancel</Button>
                <Button type="submit" disabled={submitting}>
                    {submitting ? 'Saving...' : 'Save Changes'}
                </Button>
            </div>
        </form>
    </Modal>
{/if}
