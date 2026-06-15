<script>
    import { Card, CardBody, Badge, Button, Collapse } from "@sveltestrap/sveltestrap";

    let { chunk , onApproveChunk, onDeleteChunk} = $props();

    let isOpen = $state(false);

    function toggle() {
        isOpen = !isOpen;
    }

</script>

<Card class="shadow-sm chunk-card" style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 0.75rem; overflow: hidden;">
    <CardBody class="p-0">
        <div
            class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center p-3 chunk-header"
            onclick={toggle}
            role="button"
            tabindex="0"
            onkeydown={(e) => { if(e.key === 'Enter') toggle(); }}
        >
            <div class="d-flex align-items-center gap-3 mb-2 mb-md-0">
                <h5 class="mb-0 fw-bold text-nowrap">Chunk #{chunk.chunkIndex}</h5>
                <Badge color="danger" class="text-uppercase py-1">
                    {chunk.securityStatus}
                </Badge>
            </div>
            
            <div class="text-muted flex-grow-1 mx-md-4 mb-2 mb-md-0" style="font-size: 0.95rem;">
                {chunk.securityReason}
            </div>
            
            <Button
                color="light" 
                size="sm" 
                class="align-self-end align-self-md-center toggle-btn"
            >
                {isOpen ? 'Close' : 'Inspect'}
            </Button>
        </div>

        <Collapse {isOpen}>
            <div class="p-3 bg-white border-top">
                <h6 class="text-muted mb-2 fw-semibold" style="font-size: 0.8rem; text-transform: uppercase;">
                    Content
                </h6>
                <div class="code-preview-box">
                    <code>{chunk.text}</code>
                </div>
            </div>
            
            <div class="d-flex justify-content-end gap-2 p-3 border-top" style="background-color: #f8fafc;">
                <Button color="success" size="sm" class="fw-semibold px-3" onclick={onApproveChunk}>
                    Approve chunk
                </Button>
                <Button color="danger" size="sm" class="fw-semibold px-3" onclick={onDeleteChunk}>
                    Delete chunk
                </Button>
            </div>
        </Collapse>
    </CardBody>
</Card>

<style>

    .chunk-header {
        transition: background-color 0.2s ease;
        cursor: pointer;
    }

    .chunk-header:hover {
        background-color: #f8fafc;
    }
    
    .chunk-header:focus-visible {
        outline: 2px solid #3b82f6;
        outline-offset: -2px;
    }

    .code-preview-box {
        background-color: #f1f5f9; /* Grigio chiaro */
        border-left: 4px solid #ef4444; /* Bordo rosso a sinistra */
        padding: 1rem;
        border-radius: 0 0.5rem 0.5rem 0;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        font-size: 0.9rem;
        color: #334155;
        white-space: pre-wrap;
        word-wrap: break-word;
        overflow-x: auto;
        margin: 0;
    }
    
    .code-preview-box code {
        color: inherit;
    }

</style>
