<script>
    import { page } from '$app/state';
    import { onMount } from "svelte";
    import { getDocument, deleteDocument } from "$lib/api/document.js";
    import { goto } from "$app/navigation";
    import { Button, Badge, Spinner, Alert } from "@sveltestrap/sveltestrap";
    import ConfirmModal from "$lib/components/ConfirmModal.svelte";

    let fileHash = page.params.fileHash;

    let docStatus = $state({loading: false, error: null})
    let document = $state(null);
    
    let isConfirmModalOpen = $state(false);
    let confirmModalConfig = $state({
        title: "Delete Document",
        message: "Are you sure you want to delete this document?",
        confirmText: "Delete",
        confirmColor: "danger",
        onConfirm: () => {}
    });

    let loadingDelete = $state(false);

    onMount(async () => {
        docStatus.loading = true;
        docStatus.error = null;

        try {
            document = await getDocument(fileHash);
        } catch (error) {
            docStatus.error = error;
            console.error("Error fetching document details:", error);
        } finally {
            docStatus.loading = false;
        }
    });

    function promptDelete() {
        confirmModalConfig.onConfirm = handleDelete;
        isConfirmModalOpen = true;
    }

    async function handleDelete() {
        loadingDelete = true;
        try {
            await deleteDocument(fileHash);
            await goto("/app/admin/docs");
        } catch (error) {
            console.error("Error deleting document:", error);
            alert("Error deleting document: " + error.message);
        } finally {
            loadingDelete = false;
        }
    }

    let statusColor = $derived(
        document?.status === 'INDEXED' ? 'success' :
        (document?.status === 'REJECTED_SECURITY' || document?.status === 'PARTIALLY_INDEXED') ? 'danger' :
        document?.status === 'PROCESSING' ? 'warning' : 'secondary'
    );
</script>

<div class="document-detail-container">
    {#if docStatus.loading}
        <div class="d-flex justify-content-center p-5">
            <Spinner color="primary" />
        </div>
    {:else if docStatus.error}
        <Alert color="danger" class="shadow-sm mt-3">Error while loading document </Alert>
    {:else if document}
        <header class="page-header d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center gap-3">
                <h1 class="text-truncate" title={document.fileName}>{document.fileName}</h1>
                <Badge color={statusColor} class="text-uppercase">{document.status}</Badge>
            </div>
            <div class="d-flex gap-2">
                <Button color="danger" onclick={promptDelete} disabled={loadingDelete}>
                    {loadingDelete ? 'Deleting...' : 'Delete'}
                </Button>
            </div>
        </header>

        <div class="mb-3">
            <p class="text-muted mb-0">
                <span class="text-uppercase fw-bold me-2">{document.fileType || 'Unknown'}</span> 
                • <code class="ms-2">{document.fileHash}</code>
            </p>
        </div>

        <div class="scrollable-content">
            <div class="p-4 bg-white border rounded shadow-sm">
                <pre class="document-text">{document.text}</pre>
            </div>
        </div>
    {/if}
</div>

<ConfirmModal bind:isOpen={isConfirmModalOpen} {...confirmModalConfig} />

<style>
    .document-detail-container {
        display: flex;
        height: 100%;
        min-height: 0;
        flex-direction: column;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    }

    .page-header {
        flex: 0 0 auto;
        margin-bottom: 1rem;
    }

    .page-header h1 {
        margin: 0;
        color: #111827;
        font-size: 1.65rem;
        font-weight: 750;
        max-width: 600px;
    }

    .scrollable-content {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        padding-right: 0.5rem;
        padding-bottom: 2rem;
        scrollbar-width: thin;
    }

    .scrollable-content::-webkit-scrollbar {
        width: 6px;
    }
    
    .scrollable-content::-webkit-scrollbar-thumb {
        background-color: #cbd5e1;
        border-radius: 10px;
    }

    .document-text {
        white-space: pre-wrap;
        word-wrap: break-word;
        font-family: inherit;
        font-size: 0.95rem;
        color: #334155;
        margin: 0;
    }
</style>