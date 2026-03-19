export async function exponentialBackoffRetry<T>(
    operation: (attempt: number) => Promise<T>,
    maxRetries: number = 5,
    baseDelayMs: number = 2000
): Promise<T> {
    let lastError: Error | null = null;
    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            return await operation(attempt);
        } catch (error: unknown) {
            const err = error instanceof Error ? error : new Error(String(error));
            lastError = err;
            if (err.name === 'AbortError' || err.message === 'Auth fetch timeout') {
                throw err; // Don't retry on explicit aborts or timeouts
            }
            if (attempt < maxRetries - 1) {
                // Exponential backoff: baseDelay, 2*baseDelay, 4*baseDelay...
                const delay = Math.pow(2, attempt) * baseDelayMs; 
                console.warn(`Operation failed (attempt ${attempt + 1}/${maxRetries}), retrying in ${delay}ms...`, err);
                await new Promise(r => setTimeout(r, delay));
            }
        }
    }
    throw lastError || new Error("Operation failed after retries.");
}
