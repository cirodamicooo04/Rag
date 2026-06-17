<script>
    import { Card, CardBody, CardTitle, CardSubtitle, CardText, Button, Badge, Progress } from '@sveltestrap/sveltestrap';

    let { document, onDelete, onApprove, onSecurityStatus} = $props();

    let statusColor = $derived(
        document.status === 'INDEXED' ? 'success' :
        document.status === ('REJECTED_SECURITY' || 'PARTIALLY_INDEXED') ? 'danger' :
        document.status === 'PROCESSING' ? 'warning' : 'secondary'
    );

    let progressValue = $derived(
        document.totalChunks > 0 ? Math.round((document.indexedChunks / document.totalChunks) * 100) : 0
    );

    let isQuarantined = $derived(document.status === 'PARTIALLY_INDEXED' || document.status === 'REJECTED_SECURITY');
    let isProcessing = $derived(document.status === 'PROCESSING');
</script>

<Card class="shadow h-100" style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 0.75rem; ">
    <CardBody class="d-flex flex-column">
        <div class="d-flex justify-content-between align-items-start mb-2 gap-2">
            <CardTitle class="h6 mb-0 text-truncate fw-bold text-dark" title={document.fileName}>
                {document.fileName}
            </CardTitle>
            <Badge color={statusColor} class="text-uppercase px-2 py-1" style="font-size: 0.7em;">
                {document.status}
            </Badge>
        </div>

        <CardSubtitle class="mb-3 text-muted" style="font-size: 0.8em;">
            <span class="text-uppercase fw-bold">{document.fileType || 'Unknown'}</span>
            {#if document.fileHash}
                • <span title={document.fileHash} class="text-secondary" style="font-family: monospace;">{document.fileHash.substring(0, 10)}...</span>
            {/if}
        </CardSubtitle>

        <CardText class="flex-grow-1">
            {#if !isProcessing}
                <div class="small mb-1 d-flex justify-content-between" style="font-size: 0.85em;">
                    <span class="text-muted fw-semibold">Indexed ({document.indexedChunks}/{document.totalChunks})</span>
                    <span class="fw-bold">{progressValue}%</span>
                </div>
                <Progress value={progressValue} color="success" style="height: 6px;" class="mb-2" />
            {:else}
                <div class="small mb-1" style="font-size: 0.85em;">
                    <span class="text-warning fw-semibold">Processing...</span>
                </div>
                <Progress value={100} animated striped color="warning" style="height: 6px;" class="mb-2"/>
            {/if}


            {#if isQuarantined}
                <div class="mt-3 p-2 rounded" style="background-color: #fef2f2; border: 1px solid #fecaca;">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="text-danger fw-semibold" style="font-size: 0.85em;">
                            ⚠ Quarantined chunks
                        </span>
                        <Badge color={document.quarantinedChunks > 0 ? 'danger' : 'secondary'} pill>
                            {document.quarantinedChunks}
                        </Badge>
                    </div>
                </div>
            {/if}
        </CardText>

        <div class="d-flex mt-auto pt-3 border-top">
            {#if isQuarantined}
                <Button size="sm" color="primary" class="text-white fw-semibold" onclick={() => onSecurityStatus?.(document)}>
                    Security summary
                </Button>
            {/if}

            <div class="d-flex gap-2 ms-auto">
                {#if isQuarantined}
                    <Button size="sm" color="success" class="fw-semibold" onclick={() => onApprove?.(document)} disabled={!isQuarantined}>
                        Approve
                    </Button>
                {/if}
                <Button size="sm" color="danger" class="fw-semibold" onclick={() => onDelete?.(document)} disabled={isProcessing}>
                    Delete
                </Button>
            </div>
        </div>
    </CardBody>
</Card>