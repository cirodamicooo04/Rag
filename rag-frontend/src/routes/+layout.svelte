<script>
	import "bootstrap/dist/css/bootstrap.min.css";
	import {initKeycloak} from "$lib/auth/keycloak.js";
	import {onMount} from "svelte";

	let { children } = $props();
	let initialized = $state(false)
	let error = $state(null);

	onMount(async () => {
		try {
			await initKeycloak();
		} catch (e) {
			error = e.message;
		} finally {
			initialized = true;
		}
	});
</script>


{#if initialized}
	{@render children()}
{:else if error}
	<p class="text-danger">Errore Keycloak: {error}</p>
{/if}
