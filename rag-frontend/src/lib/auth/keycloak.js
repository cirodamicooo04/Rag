import Keycloak from 'keycloak-js';

export const keycloak = new Keycloak({
    url: 'http://localhost:8089',
    realm: 'rag-system',
    clientId: 'rag-frontend'
});

export async function initKeycloak() {
    return await keycloak.init({
        onLoad: 'check-sso',
        pkceMethod: 'S256'
    });
}

export function login() {
    return keycloak.login();
}

export function logout() {
    return keycloak.logout();
}

export function getToken() {
    return keycloak.token;
}

export function getRoles() {
    return keycloak.tokenParsed?.realm_access?.roles ?? [];
}

export function isAuthenticated(){
    return keycloak.authenticated
}