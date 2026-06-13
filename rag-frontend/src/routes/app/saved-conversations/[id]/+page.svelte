<script>
	import { page } from "$app/state";

	let conversationId = $derived(page.params.id);
</script>

<h1>Conversazione {conversationId}</h1>