<!--
    ImageUpload.svelte
    
    A reusable image upload component with:
    - Drag and drop support
    - Preview of selected/uploaded image
    - Upload progress indication
    - Remove/replace functionality
    
    Usage:
    <ImageUpload 
        imageUrl={recipe.image_url} 
        onUpload={(url) => imageUrl = url}
        onRemove={() => imageUrl = ''}
    />
-->
<script lang="ts">
    const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

    // Props
    let {
        imageUrl = '',
        onUpload,
        onRemove,
        disabled = false
    }: {
        imageUrl?: string;
        onUpload: (url: string) => void;
        onRemove: () => void;
        disabled?: boolean;
    } = $props();

    // Local state
    let uploading = $state(false);
    let error = $state('');
    let dragActive = $state(false);
    let fileInput: HTMLInputElement;

    // Handle file selection (from input or drop)
    async function handleFile(file: File) {
        // Reset error
        error = '';

        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            error = 'Please select a valid image (JPEG, PNG, GIF, or WebP)';
            return;
        }

        // Validate file size (5MB max)
        const maxSize = 5 * 1024 * 1024;
        if (file.size > maxSize) {
            error = 'Image must be smaller than 5MB';
            return;
        }

        // Upload the file
        uploading = true;
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${API_BASE}/upload/recipe-image`, {
                method: 'POST',
                body: formData,
                credentials: 'include' // Include auth cookie
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Upload failed');
            }

            const data = await response.json();
            onUpload(data.url);
        } catch (err) {
            error = err instanceof Error ? err.message : 'Upload failed';
        } finally {
            uploading = false;
        }
    }

    // Input change handler
    function handleInputChange(event: Event) {
        const input = event.target as HTMLInputElement;
        if (input.files && input.files[0]) {
            handleFile(input.files[0]);
        }
    }

    // Drag handlers
    function handleDragEnter(e: DragEvent) {
        e.preventDefault();
        dragActive = true;
    }

    function handleDragLeave(e: DragEvent) {
        e.preventDefault();
        dragActive = false;
    }

    function handleDrop(e: DragEvent) {
        e.preventDefault();
        dragActive = false;
        
        if (e.dataTransfer?.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    }

    // Click to browse
    function openFilePicker() {
        fileInput?.click();
    }

    // Remove image
    function removeImage() {
        onRemove();
        error = '';
    }
</script>

<div class="space-y-2">
    <span class="block text-sm font-medium mb-1">Recipe Image</span>
    
    {#if imageUrl}
        <!-- Image Preview -->
        <div class="relative inline-block">
            <img 
                src={imageUrl} 
                alt="Recipe preview" 
                class="max-w-xs h-40 object-cover rounded-lg border"
            />
            <button
                type="button"
                onclick={removeImage}
                disabled={disabled}
                class="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white rounded-full p-1 shadow-md transition-colors disabled:opacity-50"
                aria-label="Remove image"
            >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>
        <p class="text-sm text-muted-foreground">Click the X to remove and upload a different image</p>
    {:else}
        <!-- Upload Zone -->
        <div
            class="border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer
                   {dragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/30 hover:border-primary/50'}
                   {disabled || uploading ? 'opacity-50 cursor-not-allowed' : ''}"
            role="button"
            tabindex="0"
            ondragenter={handleDragEnter}
            ondragleave={handleDragLeave}
            ondragover={(e) => e.preventDefault()}
            ondrop={handleDrop}
            onclick={openFilePicker}
            onkeydown={(e) => e.key === 'Enter' && openFilePicker()}
        >
            {#if uploading}
                <div class="flex flex-col items-center gap-2">
                    <svg class="w-8 h-8 animate-spin text-primary" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <p class="text-sm text-muted-foreground">Uploading...</p>
                </div>
            {:else}
                <svg class="w-10 h-10 mx-auto mb-2 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p class="text-sm font-medium">Drop an image here or click to browse</p>
                <p class="text-xs text-muted-foreground mt-1">JPEG, PNG, GIF, or WebP (max 5MB)</p>
            {/if}
        </div>
    {/if}

    {#if error}
        <p class="text-sm text-destructive">{error}</p>
    {/if}

    <!-- Hidden file input -->
    <input 
        bind:this={fileInput}
        type="file" 
        accept="image/jpeg,image/png,image/gif,image/webp"
        class="hidden"
        onchange={handleInputChange}
        disabled={disabled || uploading}
    />
</div>
