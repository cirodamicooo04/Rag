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
        let message = "Request failed.";
        const text = await res.text();
        if (text) {
            try {
                const data = JSON.parse(text);
                message = data.detail || data.message || text;
                if (Array.isArray(message)) {
                    message = message.map(err => err.msg || err).join(", ");
                } else if (typeof message === 'object') {
                    message = JSON.stringify(message);
                }
            } catch {
                message = text;
            }
        }
        throw new Error(message);
    }

    const contentType = res.headers.get('content-type');

    if (contentType?.includes('application/json')) {
        return await res.json();
    }

    return null;
}
