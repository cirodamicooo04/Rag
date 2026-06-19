<script>
    import { Card, CardBody, CardTitle, CardSubtitle, CardText, Button, Badge, Progress } from '@sveltestrap/sveltestrap';

    let { document, onDelete, onApprove, onSecurityStatus, onOpenDetail, onRetry} = $props();

    let statusColor = $derived(
        document.status === 'INDEXED' ? 'success' :
        ['REJECTED_SECURITY', 'PARTIALLY_INDEXED', 'ERROR'].includes(document.status) ? 'danger' :
        document.status === 'PROCESSING' ? 'warning' : 'secondary'
    );

    let progressValue = $derived(
        document.totalChunks > 0 ? Math.round((document.indexedChunks / document.totalChunks) * 100) : 0
    );

    let isQuarantined = $derived(document.status === 'PARTIALLY_INDEXED' || document.status === 'REJECTED_SECURITY');
    let isProcessing = $derived(document.status === 'PROCESSING');
    let isError = $derived(document.status === 'ERROR');

    function handleOpenDetail() {
        if (onOpenDetail) {
            onOpenDetail();
        }
    }

    let isDeleting = $state(false);
    let isApproving = $state(false);
    let isRetrying = $state(false);

    async function handleDeleteClick(e) {
        e.stopPropagation();
        if (onDelete) {
            isDeleting = true;
            try {
                await onDelete(document);
            } catch (error) {

            } finally {
                isDeleting = false;
            }
        }
    }

    async function handleApproveClick(e) {
        e.stopPropagation();
        if (onApprove) {
            isApproving = true;
            try {
                await onApprove(document);
            } catch (error) {

            } finally {
                isApproving = false;
            }
        }
    }

    async function handleRetry(e){
        if (!isError) return;
        e.stopPropagation();

        if (onRetry) {
            isRetrying = true;
            try {
                await onRetry(document);
            } catch (error) {

            } finally {
                isRetrying = false;
            }
        }
    }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<svelte:element
    this={onOpenDetail ? 'button' : 'div'} 
    class="card-wrapper {onOpenDetail ? 'clickable' : ''}" 
    onclick={onOpenDetail ? handleOpenDetail : undefined}
>
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
                    <Button size="sm" color="primary" class="text-white fw-semibold" onclick|stopPropagation={() => onSecurityStatus?.(document)}>
                        Security summary
                    </Button>
                {/if}

                <div class="d-flex gap-2 ms-auto">
                    {#if isQuarantined}
                        <Button size="sm" color="success" class="fw-semibold" onclick={handleApproveClick} disabled={!isQuarantined || isApproving || isDeleting}>
                            {isApproving ? '...' : 'Approve'}
                        </Button>
                    {/if}
                    {#if isError}
                        <Button size="sm" color="secondary" class="fw-semibold" onclick={handleRetry} disabled={isDeleting}>
                            {isRetrying ? '...' : 'Retry'}
                        </Button>
                    {/if}
                    <Button size="sm" color="danger" class="fw-semibold" onclick={handleDeleteClick} disabled={isProcessing || isDeleting || isApproving}>
                        {isDeleting ? '...' : 'Delete'}
                    </Button>
                </div>
            </div>
        </CardBody>
    </Card>
</svelte:element>

<style>
    .card-wrapper {
        background: none;
        border: none;
        padding: 0;
        width: 100%;
        text-align: left;
        display: block;
    }

    .card-wrapper.clickable {
        cursor: pointer;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }

    .card-wrapper.clickable:hover {
        transform: translateY(-4px);
    }

    .card-wrapper.clickable:focus-visible {
        outline: 2px solid var(--bs-primary);
        outline-offset: 2px;
        border-radius: 0.375rem;
    }
</style>