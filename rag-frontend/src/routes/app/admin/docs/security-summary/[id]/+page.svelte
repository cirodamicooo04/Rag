<script>
    import { page } from '$app/state';
    import { onMount } from "svelte";
    import {getSecurityStatus, approveDocument, deleteDocument, approveChunk, deleteChunk} from "$lib/api/document.js";
    import { Spinner, Alert, Button } from "@sveltestrap/sveltestrap";
    import QuarantinedChunkCard from "$lib/components/QuarantinedChunkCard.svelte";
    import ConfirmModal from "$lib/components/ConfirmModal.svelte";
    import {goto} from "$app/navigation";

    let id = page.params.id;

    let isConfirmModalOpen = $state(false);
    let confirmModalConfig = $state({
        title: "",
        message: "",
        confirmText: "",
        confirmColor: "primary",
        onConfirm: () => {}
    });

    let securitySummary = $state(null);

    // loading
    let loadingSummary = $state(false);
    let summaryError = $state(null);

    let loading = $state(false);
    let error = $state(null);

    //approving and deleting chunks
    let loadingApprove = $state(false);
    let loadingDelete = $state(false);

    let approveError = $state(null);
    let deleteError = $state(null);

    onMount(async() => {
        loadingSummary = true;
        summaryError = null;

        try {
            securitySummary = await getSecurityStatus(id);
        } catch (error) {
            summaryError = error.message;
            console.error(error);
        } finally {
            loadingSummary = false;
        }
    });

    function promptApprove() {
        confirmModalConfig = {
            title: "Approve Document",
            message: "Are you sure you want to approve this document?",
            confirmText: "Approve",
            confirmColor: "success",
            onConfirm: handleApprove
        }
        isConfirmModalOpen = true;
    }

    function promptDelete() {
        confirmModalConfig = {
            title: "Delete Document",
            message: "Are you sure you want to delete this document?",
            confirmText: "Delete",
            confirmColor: "danger",
            onConfirm: handleDelete
        }
        isConfirmModalOpen = true;
    }

    async function handleApprove() {
        loading = true;
        error = null;

        try {
            await approveDocument(id);
            securitySummary.quarantinedChunks = [];

            setTimeout(() => {
                goto("/app/admin/docs")
            }, 1500)

        } catch (error) {
            error = error.message;
            console.error(error);
        } finally {
            loading = false;
        }
    }

    async function handleDelete() {
        loading = true;
        error = null;

        try {
            await deleteDocument(id);
            await goto("/app/admin/docs")
        } catch (error) {
            error = error.message;
            console.error(error);
        } finally {
            loading = false;
        }
    }

    function promptApproveChunk(chunkId) {
        confirmModalConfig = {
            title: "Approve Chunk",
            message: "Are you sure you want to approve this chunk?",
            confirmText: "Approve",
            confirmColor: "success",
            onConfirm: () => handleApproveChunk(chunkId)
        }
        isConfirmModalOpen = true;
    }

    function promptDeleteChunk(chunkId) {
        confirmModalConfig = {
            title: "Delete Chunk",
            message: "Are you sure you want to delete this chunk?",
            confirmText: "Delete",
            confirmColor: "danger",
            onConfirm: () => handleDeleteChunk(chunkId)
        }
        console.log(chunkId)
        isConfirmModalOpen = true;
    }

    async function handleApproveChunk(chunkId) {
        loadingApprove = true;
        approveError = null;

        try {
            await approveChunk(chunkId);
            securitySummary.quarantinedChunks = securitySummary.quarantinedChunks.filter(chunk => chunk.chunkId !== chunkId);
        } catch (error) {
            approveError = error.message;
            console.error(error);
        } finally {
            loadingApprove = false;
        }
    }

    async function handleDeleteChunk(chunkId) {
        loadingDelete = true;
        deleteError = null;

        try {
            await deleteChunk(chunkId);
            securitySummary.quarantinedChunks = securitySummary.quarantinedChunks.filter(chunk => chunk.chunkId !== chunkId);

        } catch (error) {
            deleteError = error.message;
            console.error(error);
        } finally {
            loadingDelete = false;
        }
    }
</script>

<div class="security-summary-container">
    <header class="page-header d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center gap-3">
            <h1>Security Summary</h1>
        </div>
        <div class="d-flex gap-2">
            <Button color="success" onclick={promptApprove} disabled={loading}>
                Approve
            </Button>
            <Button color="danger" onclick={promptDelete} disabled={loading}>
                Delete Document
            </Button>
        </div>
    </header>

    <div class="mb-3">
        <p class="text-muted mb-0">Document Hash: <code>{id}</code></p>
    </div>

    <div class="scrollable-content">
        {#if loadingSummary}
            <div class="d-flex justify-content-center p-5">
                <Spinner color="primary" />
            </div>
        {:else if summaryError}
            <Alert color="danger" class="shadow-sm">Failed to load security summary: {summaryError}</Alert>
        {:else if securitySummary && securitySummary.quarantinedChunks}
            <div class="d-flex flex-column">
                {#if securitySummary.quarantinedChunks.length === 0}
                    <Alert color="success" class="shadow-sm">No quarantined chunks found for this document.</Alert>
                {:else}
                    {#each securitySummary.quarantinedChunks as chunk (chunk.chunkId)}
                        <QuarantinedChunkCard {chunk} onApproveChunk={() => {promptApproveChunk(chunk.chunkId)}} onDeleteChunk={() => {promptDeleteChunk(chunk.chunkId)}} />
                    {/each}
                {/if}
            </div>
        {/if}
    </div>
</div>

<ConfirmModal bind:isOpen={isConfirmModalOpen} {...confirmModalConfig} />

<style>
    .security-summary-container {
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
</style>