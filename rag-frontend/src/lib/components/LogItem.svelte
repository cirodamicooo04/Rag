<script lang="ts">
    import { Badge, Button, Card, CardBody, CardHeader, CardFooter, Spinner } from '@sveltestrap/sveltestrap';

    interface Log {
        id: number;
        userId: string;
        originalQuery: string;
        finalQuery: string;
        blockedStage: string;
        blockedBy: string;
        reason: string;
        createdAt: string;
    }

    let { log, onDelete }: { log: Log, onDelete: (id: number) => Promise<void> } = $props();

    let isDeleting = $state(false);
    let errorMessage = $state<string | null>(null);

    async function handleDeleteClick() {
        isDeleting = true;
        errorMessage = null;
        
        try {
            await onDelete(log.id);
        } catch (e: any) {
            errorMessage = "Failed to delete log";
            console.log("Error deleting log:", e);
            isDeleting = false;
        }
    }
</script>

<Card class="mb-4 shadow-sm">
    <CardHeader class="d-flex justify-content-between align-items-center bg-light">
        <span class="fw-bold">ID: {log.id}</span>
        <span class="text-muted small">
            <strong>Created At:</strong> {new Date(log.createdAt).toLocaleString()}
        </span>
    </CardHeader>
    <CardBody>
        <div class="row mb-3">
            <div class="col-md-6 mb-2 mb-md-0">
                <strong>User ID:</strong> <span class="text-secondary">{log.userId}</span>
            </div>
            <div class="col-md-6 d-flex gap-2 align-items-center">
                <strong>Blocked Stage:</strong> <Badge color="warning">{log.blockedStage}</Badge>
                <strong class="ms-2">Blocked By:</strong> <Badge color="danger">{log.blockedBy}</Badge>
            </div>
        </div>

        <div class="mb-4">
            <strong>Reason:</strong> <span class="text-secondary">{log.reason}</span>
        </div>

        <div class="mb-0 p-3 border rounded border-primary bg-primary bg-opacity-10">
            <strong class="text-primary d-block mb-2">Original Query:</strong>
            <p class="mb-0 text-wrap text-break" style="white-space: pre-wrap;">{log.originalQuery}</p>
        </div>

    </CardBody>
    <CardFooter class="bg-white">
        <div class="d-flex justify-content-end align-items-center gap-3">
            {#if errorMessage}
                <span class="text-danger small fw-semibold m-0">
                    <i class="bi bi-exclamation-circle me-1"></i>{errorMessage}
                </span>
            {/if}
            <Button color="danger" disabled={isDeleting} on:click={handleDeleteClick}>
                {#if isDeleting}
                    <Spinner size="sm" class="me-2" /> Deleting...
                {:else}
                    Delete
                {/if}
            </Button>
        </div>
    </CardFooter>
</Card>
