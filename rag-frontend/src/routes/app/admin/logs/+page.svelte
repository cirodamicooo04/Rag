<script lang="ts">
    import { onMount } from "svelte";
    import { getLogs , clearLogs, deleteLog} from "$lib/api/log.js";
    import { Button, Spinner } from "@sveltestrap/sveltestrap";
    import LogItem from "$lib/components/LogItem.svelte";

    let logs = $state([]);

    let loading = $state(true);
    let error = $state(null);

    let clearLogsLoading = $state(false);
    let clearLogsError = $state(null);


    onMount(async () => {
        loading = true;
        error = null;

        try {
            logs = await getLogs();
        } catch (e) {
            error = e;
            console.log(e);
        } finally {
            loading = false;
        }
    });

    async function handleDelete(id: number) {
        await deleteLog(id);
        logs = logs.filter(log => log.id !== id);
    }

    async function handleClearLogs() {
        clearLogsLoading = true;
        clearLogsError = null;

        try {
            await clearLogs()
            logs = [];
        } catch (e) {
            clearLogsError = e;
            console.log(e);
        } finally {
            clearLogsLoading = false;
        }
    }

</script>

<div class="logs-container">
    <header class="page-header d-flex align-items-center justify-content-between">
        <h1>Logs</h1>
        
        <div class="d-flex align-items-center gap-3">
            {#if clearLogsError}
                <span class="text-danger small fw-semibold m-0">
                    <i class="bi bi-exclamation-circle me-1"></i>Failed to clear logs
                </span>
            {/if}
            <Button color="danger" disabled={loading || error || logs.length === 0 || clearLogsLoading} onclick={handleClearLogs}>
                {#if clearLogsLoading}
                    <Spinner size="sm" class="me-2" /> Clearing...
                {:else}
                    Clear logs
                {/if}
            </Button>
        </div>
    </header>

    <div class="scrollable-content">
        {#if loading}
            <div class="loading-state">
                <p>Loading logs...</p>
                <Spinner color="primary" class="mt-2" />
            </div>
        {:else if error}
            <div class="error-state">
                <p>Failed to load logs.</p>
            </div>
        {:else if logs.length === 0}
            <div class="empty-state">
                <p>No logs found.</p>
            </div>
        {:else}
            <div class="logs-list">
                {#each logs as log (log.id)}
                    <LogItem {log} onDelete={handleDelete} />
                {/each}
            </div>
        {/if}
    </div>
</div>

<style>
    .logs-container {
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

    .logs-list {
        display: flex;
        flex-direction: column;
    }

    .loading-state, .error-state, .empty-state {
        text-align: center;
        padding: 3rem;
        background: #f8fafc;
        border-radius: 0.75rem;
        color: #64748b;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .error-state {
        background: #fef2f2;
        color: #ef4444;
        border: 1px solid #fecaca;
    }
</style>