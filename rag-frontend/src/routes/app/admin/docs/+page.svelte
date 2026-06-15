<script>
    import { onMount } from "svelte";
    import { getDocuments, deleteDocument, approveDocument } from "$lib/api/document.js";
    import DocCard from "$lib/components/DocCard.svelte";
    import { goto } from "$app/navigation";
    import { Button} from "@sveltestrap/sveltestrap";
    import ConfirmModal from "$lib/components/ConfirmModal.svelte";

    let docs = $state([]);
    
    // Modal state
    let isConfirmModalOpen = $state(false);
    let confirmModalConfig = $state({
        title: "",
        message: "",
        confirmText: "",
        confirmColor: "primary",
        onConfirm: () => {}
    });

    let loadingDocs = $state(false);
    let loadingDocsError = $state(null);

    //deleting
    let deletingLoading = $state(false);
    let deletingError = $state(null);

    //deleting_dataset
    let deletingDatasetLoading = $state(false);
    let deletingDatasetError = $state(null);

    //approving
    let approvingLoading = $state(false);
    let approvingError = $state(null);

    onMount(async() => {
        await loadDocs();
    });

    async function loadDocs(){
        loadingDocs = true;
        loadingDocsError = null;

        try {
            docs = await getDocuments();
        } catch(e) {
            loadingDocsError = e.message;
            console.error(e);
        } finally {
            loadingDocs = false;
        }
    }

    function promptDelete(id) {
        confirmModalConfig = {
            title: "Delete document",
            message: "Do you really want to delete this document?",
            confirmText: "Delete",
            confirmColor: "danger",
            onConfirm: () => handleDelete(id)
        };
        isConfirmModalOpen = true;
    }

    async function handleDelete(id){
        deletingLoading = true;
        deletingError = null;

        try {
            await deleteDocument(id);
            docs = docs.filter(doc => doc.fileHash !== id);
        } catch (e) {
            deletingError = e.message;
            console.error(e);
        } finally {
            deletingLoading = false;
        }
    }

    function promptApprove(id) {
        confirmModalConfig = {
            title: "Approve document",
            message: "Do you really want to approve this document?",
            confirmText: "Approve",
            confirmColor: "success",
            onConfirm: () => handleApprove(id)
        };
        isConfirmModalOpen = true;
    }

    async function handleApprove(id){
        approvingLoading = true;
        approvingError = null;

        try {
            await approveDocument(id);
            await loadDocs(); // Ricarichiamo perché lo stato generale potrebbe essere cambiato
        } catch (e) {
            approvingError = e.message;
            console.error(e);
        } finally {
            approvingLoading = false;
        }
    }

    function promptDeleteDataset() {
        confirmModalConfig = {
            title: "Delete dataset",
            message: "Do you really want to delete the dataset?",
            confirmText: "Delete",
            confirmColor: "danger",
            onConfirm: handleDeleteDataset
        };
        isConfirmModalOpen = true;
    }

    async function handleDeleteDataset(){
        deletingDatasetLoading = true;
        deletingDatasetError = null;

        try {
            await deleteDataset()
            docs = []

        } catch (e) {
            deletingDatasetError = e.message;
            console.error(e);
        } finally {
            deletingDatasetLoading = false;
        }
    }
</script>

<div class="documents-container">
    <header class="page-header d-flex align-items-center justify-content-between">
        <h1>Documents</h1>
        <div class="d-flex gap-2">
            <Button color="danger" onclick={promptDeleteDataset} disabled={deletingDatasetLoading || docs.length === 0}>
                Delete dataset
            </Button>
            <Button color="primary" class="fw-semibold shadow-sm" onclick={() => {/* TODO: Logica modale */}}>
                +
            </Button>
        </div>
    </header>
    
    <div class="scrollable-content">
        {#if loadingDocs}
            <div class="loading-state">
                <p>Loading documents...</p>
            </div>
        {:else if loadingDocsError}
            <div class="error-state">
                <p>Failed to load documents. Please try again</p>
            </div>
        {:else if docs.length === 0}
            <div class="empty-state">
                <p>No documents found.</p>
            </div>
        {:else}
            <div class="documents-grid">
                {#each docs as doc}
                    <DocCard document={doc}
                             onApprove={() => {promptApprove(doc.fileHash)}}
                             onDelete={() => {promptDelete(doc.fileHash)}}
                             onSecurityStatus={() => goto(`/app/admin/docs/security-summary/${doc.fileHash}`)}
                    />
                {/each}
            </div>
        {/if}
    </div>
</div>

<ConfirmModal 
    bind:isOpen={isConfirmModalOpen}
    title={confirmModalConfig.title}
    message={confirmModalConfig.message}
    confirmText={confirmModalConfig.confirmText}
    confirmColor={confirmModalConfig.confirmColor}
    onConfirm={confirmModalConfig.onConfirm}
/>

<style>
    .documents-container {
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