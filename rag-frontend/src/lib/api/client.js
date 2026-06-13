import { keycloak, login } from '$lib/auth/keycloak.js';

const API_BASE_URL = 'http://localhost:8000/api/v1';

async function getTokenForRequest(auth) {
    if (!keycloak.authenticated) {
        if (auth === "required") {
            await login();
            throw new Error("Authentication required.");
        }

        return null;
    }

    try {
        await keycloak.updateToken(30);
        return keycloak.token ?? null;
    } catch {
        if (auth === "required") {
            await login();
            throw new Error("Session expired. Please sign in again.");
        }

        return null;
    }
}

export async function apiFetch(path, options = {}) {
    const {auth = "optional", headers: optionHeaders, ...fetchOptions} = options;
    const token = await getTokenForRequest(auth);

    const headers = {
        ...(optionHeaders ?? {})
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE_URL}${path}`, {
        ...fetchOptions,
        headers
    });

    if (res.status === 401 && auth === "required") {
        await login();
        throw new Error("Session expired. Please sign in again.");
    }

    if (res.status === 401) {
        throw new Error("Unauthorized request.");
    }

    if (res.status === 403) {
        throw new Error("Forbidden request.");
    }

    if (!res.ok) {
        const message = await res.text();
        throw new Error(message || "Request failed.");
    }

    const contentType = res.headers.get('content-type');

    if (contentType?.includes('application/json')) {
        return await res.json();
    }

    return null;
}
