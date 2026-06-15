<script>
    import { Modal, ModalBody, ModalFooter, ModalHeader, Button } from '@sveltestrap/sveltestrap';

    let {
        isOpen = $bindable(false),
        title = "Conferma Azione",
        message = "Sei sicuro di voler procedere?",
        confirmText = "Conferma",
        cancelText = "Annulla",
        confirmColor = "primary",
        onConfirm,
        onCancel
    } = $props();

    function toggle() {
        isOpen = !isOpen;
    }

    function handleConfirm() {
        if (onConfirm) onConfirm();
        isOpen = false;
    }

    function handleCancel() {
        if (onCancel) onCancel();
        isOpen = false;
    }
</script>

<Modal {isOpen} {toggle}>
    <ModalHeader {toggle}>{title}</ModalHeader>
    <ModalBody>
        {message}
    </ModalBody>
    <ModalFooter>
        <Button color="light" on:click={handleCancel}>{cancelText}</Button>
        <Button color={confirmColor} on:click={handleConfirm}>{confirmText}</Button>
    </ModalFooter>
</Modal>
