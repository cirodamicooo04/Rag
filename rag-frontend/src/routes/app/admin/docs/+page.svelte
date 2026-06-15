<script>
    import { onMount } from "svelte";
    import { getDocuments, deleteDocument, approveDocument } from "$lib/api/document.js";
    import DocCard from "$lib/components/DocCard.svelte";
    import { goto } from "$app/navigation";
    import { Button} from "@sveltestrap/sveltestrap";

    let docs = $state([]);

    let loading_docs = $state(false);
    let loading_docs_error = $state(null);

    //deleting
    let deleting_loading = $state(false);
    let deleting_error = $state(null);

    //approving
    let approving_loading = $state(false);
    let approving_error = $state(null);

    onMount(async() => {
        await loadDocs();
    });

    async function loadDocs(){
        loading_docs = true;
        loading_docs_error = null;

        try {
            docs = await getDocuments();
        } catch(e) {
            loading_docs_error = e.message;
            console.error(e);
        } finally {
            loading_docs = false;
        }
    }

    //TODO: Aggiungere finestra modale per conferma
    async function handleDelete(id){
        deleting_loading = true;
        deleting_error = null;

        try {
            await deleteDocument(id);
            docs = docs.filter(doc => doc.fileHash !== id);
        } catch (e) {
            deleting_error = e.message;
            console.error(e);
        } finally {
            deleting_loading = false;
        }
    }

    //TODO: Aggiungere finestra modale per conferma
    async function handleApprove(id){
        approving_loading = true;
        approving_error = null;

        try {
            await approveDocument(id);
            await loadDocs(); // Ricarichiamo perché lo stato generale potrebbe essere cambiato
        } catch (e) {
            approving_error = e.message;
            console.error(e);
        } finally {
            approving_loading = false;
        }
    }
</script>

<div class="documents-container">
    <header class="page-header d-flex justify-content-between align-items-center">
        <h1>Documents</h1>
        <Button color="primary" class="fw-semibold shadow-sm" on:click={() => {/* Qui metterai la logica per aprire la modale */}}>
            +
        </Button>
    </header>
    
    <div class="scrollable-content">
        {#if loading_docs}
            <div class="loading-state">
                <p>Caricamento documenti in corso...</p>
            </div>
        {:else if loading_docs_error}
            <div class="error-state">
                <p>{loading_docs_error}</p>
            </div>
        {:else if docs.length === 0}
            <div class="empty-state">
                <p>Nessun documento trovato.</p>
            </div>
        {:else}
            <div class="documents-grid">
                {#each docs as doc}
                    <DocCard document={doc}
                             onApprove={() => {handleApprove(doc.fileHash)}}
                             onDelete={() => {handleDelete(doc.fileHash)}}
                             onSecurityStatus={() => goto(`/app/admin/docs/${doc.fileHash}`)}
                             canApprove={doc.status === "PARTIALLY_INDEXED" || doc.status === "REJECTED_SECURITY"}
                    />
                {/each}
            </div>
        {/if}
    </div>
</div>

<style>
    .documents-container {
        width: 100%;
        height: 100%;
        padding: 1.5rem 0.5rem 1.5rem 1.5rem;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    }

    .page-header {
        margin-bottom: 2rem;
        text-align: left;
        flex-shrink: 0; 
        padding-right: 1rem;
    }

    .page-header h1 {
        font-size: 2rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0;
    }

    .scrollable-content {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        padding: 1.5rem 1.5rem 2rem 1.5rem;
        scrollbar-width: thin;
    }

    .scrollable-content::-webkit-scrollbar {
        width: 6px;
    }
    
    .scrollable-content::-webkit-scrollbar-thumb {
        background-color: #cbd5e1;
        border-radius: 10px;
    }

    .documents-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1.5rem;
        width: 100%;
        align-content: start;
    }

    .loading-state, .error-state, .empty-state {
        text-align: center;
        padding: 3rem;
        background: #f8fafc;
        border-radius: 0.75rem;
        color: #64748b;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .error-state {
        background: #fef2f2;
        color: #ef4444;
        border: 1px solid #fecaca;
    }
</style>