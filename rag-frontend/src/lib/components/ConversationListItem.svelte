<script>
    import { Button, ListGroupItem } from "@sveltestrap/sveltestrap";

    let {conversation, onDelete, onOpen, disabled = false} = $props();

    let title = $derived(conversation?.title ?? "Untitled conversation");
    let preview = $derived(getLastMessagePreview(conversation));

    //TODO: Aggiustare prendendo l'ultimo messaggio dell'utente
    function getLastMessagePreview(conversation) {
        const messages = conversation?.messages ?? conversation?.conversation_messages ?? [];

        if (!Array.isArray(messages) || messages.length === 0) {
            return "Nessun messaggio disponibile";
        }

        const lastMessage = messages[messages.length - 1];
        const content = getMessageContent(lastMessage).replace(/\s+/g, " ").trim();

        if (!content) {
            return "Nessun messaggio disponibile";
        }

        const role = lastMessage?.role === "user" ? "Tu: " : lastMessage?.role === "assistant" ? "Assistente: " : "";
        return `${role}${content}`;
    }

    function getMessageContent(message) {
        if (typeof message === "string") return message;
        return message?.content ?? message?.text ?? message?.message ?? message?.answer ?? "";
    }
</script>

<ListGroupItem class="conversation-list-item">
    <div class="conversation-copy">
        <h2 class="conversation-title">{title}</h2>
        <p class="conversation-preview">{preview}</p>
    </div>

    <div class="conversation-actions">
        <Button color="primary" size="sm" outline onclick={onOpen} {disabled}>
            Apri
        </Button>
        <Button color="danger" size="sm" outline onclick={onDelete} {disabled}>
            Elimina
        </Button>
    </div>
</ListGroupItem>

<style>
    :global(.conversation-list-item) {
        display: flex;
        align-items: stretch;
        gap: 1rem;
        padding: 1rem;
    }

    .conversation-copy {
        min-width: 0;
        flex: 1;
    }

    .conversation-title {
        margin: 0 0 0.35rem;
        color: #111827;
        font-size: 1rem;
        font-weight: 700;
        line-height: 1.25;
    }

    .conversation-preview {
        display: -webkit-box;
        margin: 0;
        overflow: hidden;
        color: #6b7280;
        font-size: 0.9rem;
        line-height: 1.35;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
    }

    .conversation-actions {
        display: flex;
        flex: 0 0 auto;
        align-items: flex-end;
        justify-content: flex-end;
        gap: 0.5rem;
        margin-left: auto;
    }

    @media (max-width: 640px) {
        :global(.conversation-list-item) {
            flex-direction: column;
        }

        .conversation-actions {
            width: 100%;
        }
    }
</style>
