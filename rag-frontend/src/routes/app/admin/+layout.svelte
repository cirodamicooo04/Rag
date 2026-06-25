<script>
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { getRoles } from "$lib/auth/keycloak.js";

    let { children } = $props();
    let isAuthorized = $state(false);

    onMount(() => {
        // Verifica se l'utente ha il ruolo ADMIN
        if (!getRoles().includes("ADMIN")) {
            goto("/app"); // Reindirizza gli utenti non autorizzati
        } else {
            isAuthorized = true;
        }
    });
</script>

{#if isAuthorized}
    {@render children()}
{:else}
    <div class="d-flex justify-content-center p-5">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Verifica autorizzazioni...</span>
        </div>
    </div>
{/if}
