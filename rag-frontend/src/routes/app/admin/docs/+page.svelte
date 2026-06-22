<script>
    import { onMount } from "svelte";
    import {
        getDocuments,
        deleteDocument,
        approveDocument,
        uploadDocument,
        getProcessingDocumentsStatus,
        retryDocument
    } from "$lib/api/document.js";
    import DocCard from "$lib/components/DocCard.svelte";
    import { goto } from "$app/navigation";
    import {Alert, Badge, Button, Input, Modal, ModalBody, ModalFooter, ModalHeader, TabContent, TabPane, Toast, ToastBody, ToastHeader} from "@sveltestrap/sveltestrap";
    import ConfirmModal from "$lib/components/ConfirmModal.svelte";
    import {fade} from "svelte/transition";

    let docs = $state([]);

    let readyDocs = $state([])
    let processingDocs = $state([])
    let quarantineDocs = $state([])
    let errorDocs = $state([])

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


    //deleting_dataset
    let deletingDatasetLoading = $state(false);
    let deletingDatasetError = $state(null);


    let isModalOpen = $state(false);
    let selectedFile = $state(null);
    let uploadStatus = $state({loading: false, error: null, success: false});

    //TOAST
    let toasts = $state([]);

    $effect(() => {
        if (processingDocs.length === 0){
            return;
        }

        const interval = setInterval(async () => {
            try {
                const docs = await getProcessingDocumentsStatus(processingDocs.map(doc => doc.fileHash));

                docs.forEach(doc => {
                    if (doc.status === "ERROR"){
                        processingDocs = processingDocs.filter(d => d.fileHash !== doc.fileHash);
                        errorDocs.push(doc);
                        showToast(doc, false, true)
                    } else if (doc.status !== "PROCESSING"){
                        processingDocs = processingDocs.filter(d => d.fileHash !== doc.fileHash);
                        if (doc.status === "INDEXED"){
                            readyDocs.push(doc)
                            showToast(doc, true);
                        } else {
                            quarantineDocs.push(doc)
                            showToast(doc, false);
                        }
                    }
                })
            } catch (e) {
                console.error("Error while polling for processing docs", e)
            }
        }, 2500)

        return () => clearInterval(interval);
    })

    function showToast(doc, success = true, error = false){
        //id casuale univoco
        const id = Date.now() + Math.random();

        let titleString = success ? "Document processed" : "Security warning";
        let messageString = success ? `Document ${doc.fileName} processed successfully` : `Document ${doc.fileName} has been processed with security warnings.`;
        if (!success && error){
            titleString = "Error while processing document"
            messageString = `An error occurred while processing the document ${doc.fileName}. Please try again later.`
        }

        const newToast = {
            id,
            title: titleString,
            message: messageString,
            color: success ? "success" : "danger",
            isOpen: true
        };
        
        toasts.push(newToast);

        setTimeout(() => {
            removeToast(id);
        }, 3500)
    }

    function removeToast(id) {
        toasts = toasts.filter(t => t.id !== id);
    }


    function toggle(){
        if (isModalOpen){
            selectedFile = null;
            uploadStatus = {error: null, success: false};
        }
        isModalOpen = !isModalOpen;
    }

    async function handleUpload() {
        uploadStatus.loading = true;
        uploadStatus.error = null;
        uploadStatus.success = null;

        try {
            let formData = new FormData();
            formData.append("file", selectedFile[0]);
            const response = await uploadDocument(formData);
            processingDocs.push(response);

            uploadStatus.success = true;
        } catch (e) {
            uploadStatus.error = e.message;
            console.error(e);
        } finally {
            uploadStatus.loading = false;
        }
    }

    onMount(async() => {
        await loadDocs();
    });

    async function loadDocs(){
        loadingDocs = true;
        loadingDocsError = null;

        try {
            const response = await getDocuments();
            
            readyDocs = [];
            processingDocs = [];
            quarantineDocs = [];
            errorDocs = [];
            
            response.forEach(doc => {
                if (doc.status === "INDEXED"){
                    readyDocs.push(doc)
                } else if (doc.status === "REJECTED_SECURITY" || doc.status === "PARTIALLY_INDEXED"){
                    quarantineDocs.push(doc)
                } else if (doc.status === "ERROR") {
                    errorDocs.push(doc)
                } else {
                    processingDocs.push(doc)
                }
            });
            
            docs = response;

        } catch(e) {
            loadingDocsError = e.message;
            console.error(e);
        } finally {
            loadingDocs = false;
        }
    }

    function promptDelete(id) {
        return new Promise((resolve, reject) => {
            confirmModalConfig = {
                title: "Delete document",
                message: "Do you really want to delete this document?",
                confirmText: "Delete",
                confirmColor: "danger",
                onConfirm: async () => {
                    try {
                        await handleDelete(id);
                        resolve();
                    } catch (e) {
                        reject(e);
                    }
                },
                onCancel: () => reject(new Error("Cancelled"))
            };
            isConfirmModalOpen = true;
        });
    }

    async function handleDelete(id){
        try {
            await deleteDocument(id);
            docs = docs.filter(doc => doc.fileHash !== id);
            readyDocs = readyDocs.filter(doc => doc.fileHash !== id);
            processingDocs = processingDocs.filter(doc => doc.fileHash !== id);
            quarantineDocs = quarantineDocs.filter(doc => doc.fileHash !== id);
            errorDocs = errorDocs.filter(doc => doc.fileHash !== id);
        } catch (e) {
            console.error(e);
            throw e; // Propagate the error so the Promise in promptDelete is rejected
        }
    }

    async function handleRetry(id) {
        try {
            const doc = await retryDocument(id);
            errorDocs = errorDocs.filter(d => d.fileHash !== id);
            processingDocs.push(doc);
        } catch (e) {
            console.error(e);
            throw e;
        }
    }

    function promptApprove(id) {
        return new Promise((resolve, reject) => {
            confirmModalConfig = {
                title: "Approve document",
                message: "Do you really want to approve this document?",
                confirmText: "Approve",
                confirmColor: "success",
                onConfirm: async () => {
                    try {
                        await handleApprove(id);
                        resolve();
                    } catch (e) {
                        reject(e);
                    }
                },
                onCancel: () => reject(new Error("Cancelled"))
            };
            isConfirmModalOpen = true;
        });
    }

    async function handleApprove(id){
        try {
            await approveDocument(id);
            await loadDocs(); // Ricarichiamo perché lo stato generale potrebbe essere cambiato
        } catch (e) {
            console.error(e);
            throw e; // Propagate the error so the Promise in promptApprove is rejected
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
            docs = [];
            readyDocs = [];
            processingDocs = [];
            quarantineDocs = [];
            errorDocs = [];

        } catch (e) {
            deletingDatasetError = e.message;
            console.error(e);
        } finally {
            deletingDatasetLoading = false;
        }
    }

</script>

<!--- UPLOADING FILE MODAL -->
<Modal isOpen={isModalOpen} toggle={toggle} title="Upload new file" centered={true}>
    <ModalHeader>
        <h5><strong>Upload new file</strong></h5>
    </ModalHeader>
    <ModalBody>
        {#if uploadStatus.error}
            <Alert color="danger">Error while uploading file</Alert>
        {/if}
        {#if uploadStatus.success}
            <Alert color="success">File uploaded with success</Alert>
        {/if}

        <Input type="file" bind:files={selectedFile} accept=".txt" disabled={uploadStatus.loading || uploadStatus.success}/>

        {#if selectedFile}
            <div class="pt-3">
                <strong class="text-success">File ready to upload</strong>
            </div>

        {/if}
    </ModalBody>

    <ModalFooter>
        <Button color="primary" disabled={uploadStatus.loading || !selectedFile || uploadStatus.success} onclick={handleUpload}>
            Upload
        </Button>

        <Button color="secondary" onclick={toggle} disabled={uploadStatus.loading}>
            Cancel
        </Button>
    </ModalFooter>

</Modal>


<div class="documents-container">
    <header class="page-header d-flex align-items-center justify-content-between">
        <h1>Documents</h1>
        <div class="d-flex gap-2">
            <Button color="danger" onclick={promptDeleteDataset} disabled={deletingDatasetLoading || docs.length === 0}>
                Delete dataset
            </Button>
            <Button color="primary" class="fw-semibold shadow-sm" disabled={loadingDocs || loadingDocsError} onclick={toggle}>
                +
            </Button>
        </div>
    </header>

    {#if loadingDocs}
        <div class="loading-state">
            <p>Loading documents...</p>
        </div>
    {:else if loadingDocsError}
        <div class="error-state">
            <p>Failed to load documents. Please try again</p>
        </div>
    {:else}
        <TabContent>
            <!-- READY TAB -->
            <TabPane tabId="ready" active>
                <span slot="tab" class="fw-bold">
                    Ready
                    <Badge color="primary" class="ms-1">{readyDocs.length}</Badge>
                </span>
                <div class="scrollable-content mt-3">
                    {#if readyDocs.length === 0}
                        <div class="empty-state">
                            <p>No ready documents found.</p>
                        </div>
                    {:else}
                        <div class="documents-grid">
                            {#each readyDocs as doc (doc.fileHash)}
                                <DocCard document={doc}
                                         onApprove={() => {promptApprove(doc.fileHash)}}
                                         onDelete={() => {promptDelete(doc.fileHash)}}
                                         onSecurityStatus={() => goto(`/app/admin/docs/security-summary/${doc.fileHash}`)}
                                         onOpenDetail={() => goto('/app/admin/docs/' + doc.fileHash)}
                                />
                            {/each}
                        </div>
                    {/if}
                </div>
            </TabPane>

            <!-- PROCESSING TAB -->
            <TabPane tabId="processing">
                <span slot="tab" class="fw-bold text-primary">
                    Processing 
                    {#if processingDocs.length > 0}
                        <Badge color="primary" class="ms-1">{processingDocs.length}</Badge>
                    {/if}
                </span>
                <div class="scrollable-content mt-3">
                    {#if processingDocs.length === 0}
                        <div class="empty-state">
                            <p>No documents in processing.</p>
                        </div>
                    {:else}
                        <div class="documents-grid">
                            {#each processingDocs as doc (doc.fileHash)}
                                <!-- Passiamo isProcessing al componente (se lo supporta) -->
                                <DocCard document={doc}
                                         onApprove={() => {promptApprove(doc.fileHash)}}
                                         onDelete={() => {promptDelete(doc.fileHash)}}
                                         onSecurityStatus={() => goto(`/app/admin/docs/security-summary/${doc.fileHash}`)}
                                />
                            {/each}
                        </div>
                    {/if}
                </div>
            </TabPane>

            <!-- QUARANTINE TAB -->
            <TabPane tabId="quarantine">
                <span slot="tab" class="fw-bold text-danger">
                    Quarantine 
                    {#if quarantineDocs.length > 0}
                        <Badge color="danger" class="ms-1">{quarantineDocs.length}</Badge>
                    {/if}
                </span>
                <div class="scrollable-content mt-3">
                    {#if quarantineDocs.length === 0}
                        <div class="empty-state">
                            <p>No quarantined documents.</p>
                        </div>
                    {:else}
                        <div class="documents-grid">
                            {#each quarantineDocs as doc (doc.fileHash)}
                                <DocCard document={doc}
                                         onApprove={() => {promptApprove(doc.fileHash)}}
                                         onDelete={() => {promptDelete(doc.fileHash)}}
                                         onSecurityStatus={() => goto(`/app/admin/docs/security-summary/${doc.fileHash}`)}
                                         onOpenDetail={() => goto('/app/admin/docs/' + doc.fileHash)}
                                />
                            {/each}
                        </div>
                    {/if}
                </div>
            </TabPane>

            <!-- ERROR TAB -->
            <TabPane tabId="error">
                <span slot="tab" class="fw-bold text-danger">
                    Failed
                    {#if errorDocs.length > 0}
                        <Badge color="danger" class="ms-1">{errorDocs.length}</Badge>
                    {/if}
                </span>
                <div class="scrollable-content mt-3">
                    {#if errorDocs.length === 0}
                        <div class="empty-state">
                            <p>No documents in error state.</p>
                        </div>
                    {:else}
                        <div class="documents-grid">
                            {#each errorDocs as doc (doc.fileHash)}
                                <DocCard document={doc}
                                         onDelete={() => {promptDelete(doc.fileHash)}}
                                         onRetry={() => {handleRetry(doc.fileHash)}}
                                />
                            {/each}
                        </div>
                    {/if}
                </div>
            </TabPane>

        </TabContent>
    {/if}
</div>


<div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 1055;">
    {#each toasts as toast (toast.id)}
        <div transition:fade={{duration: 200}}>
            <Toast isOpen={toast.isOpen} class="mb-3 shadow-sm border-{toast.color}">
                <ToastHeader toggle={() => removeToast(toast.id)} icon={toast.color}>
                    <strong class="me-auto text-{toast.color}">{toast.title}</strong>
                </ToastHeader>
                <ToastBody>
                    {toast.message}
                </ToastBody>
            </Toast>
        </div>
    {/each}
</div>

<ConfirmModal 
    bind:isOpen={isConfirmModalOpen}
    title={confirmModalConfig.title}
    message={confirmModalConfig.message}
    confirmText={confirmModalConfig.confirmText}
    confirmColor={confirmModalConfig.confirmColor}
    onConfirm={confirmModalConfig.onConfirm}
    onCancel={confirmModalConfig.onCancel}
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

    :global(.tab-content) {
        display: flex;
        flex-direction: column;
        flex: 1;
        min-height: 0;
    }

    :global(.tab-pane.active) {
        display: flex;
        flex-direction: column;
        flex: 1;
        min-height: 0;
    }

    .scrollable-content {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        padding-right: 0.5rem;
        padding-bottom: 2rem;
        padding-top: 1rem;
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