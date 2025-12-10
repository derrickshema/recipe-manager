interface FormErrors {
    [key: string]: string[];
}

export function applyFormErrors(errors: FormErrors) {
    // Convert API validation errors to form-friendly format
    return Object.entries(errors).reduce((acc, [field, messages]) => {
        acc[field] = Array.isArray(messages) ? messages[0] : messages;
        return acc;
    }, {} as Record<string, string>);
}