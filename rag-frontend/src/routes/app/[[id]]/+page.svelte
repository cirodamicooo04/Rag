<script>
    import {Alert, Badge, Button, Input, Modal, ModalBody, ModalFooter, ModalHeader, Collapse} from "@sveltestrap/sveltestrap"
    import {ask, askDebug} from "$lib/api/ask.js"
    import {getConversation, save_conversation} from "$lib/api/conversation.js"
    import {getRoles} from "$lib/auth/keycloak.js"
    import {page} from "$app/state"

    let query = $state("")
    let messages = $state([])
    let sequence_number = $state(0)

    let isAdmin = $state(false)
    let debugMode = $state(false)

    $effect(() => {
        isAdmin = getRoles().includes("ADMIN")
    })

    // colleghiamo il div dei messaggi per lo scroll automatico
    let chatContainer;

    // auto scroll effect
    $effect(() => {
        const trigger = messages.length;

        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    });

    let loading = $state(false)
    let error = $state(null)

    //modal
    let modalOpen = $state(false);
    const toggle = () => (modalOpen = !modalOpen);

    let conversation_title = $state("")
    let saving_conversations_loading = $state(false)
    let saving_conversations_error = $state(null)
    let saving_conversations_success = $state(null)

    let loading_conversation = $state(false)
    let loading_conversation_error = $state(null)

    const DRAFT_KEY = "rag_chat_draft";

    $effect(() => {
        const id = page.params.id;

        if (id) {
            loadConversation(id);
        } else {
            //proviamo a caricare i messaggi salvati nel sessionStorage
            const savedDraft = sessionStorage.getItem(DRAFT_KEY);
            if (savedDraft) {
                let parsedMessages = JSON.parse(savedDraft);
                parsedMessages.sort((a, b) => a.sequence_number - b.sequence_number);
                sequence_number = parsedMessages.length > 0 ? Math.max(...parsedMessages.map(m => m.sequence_number)) : 0;
                messages = parsedMessages;
            } else {
                messages = [];
                sequence_number = 0;
                conversation_title = "";
            }
        }
    });

    //salvataggio dei messaggi nel sessionStorage ogni cambio di stato dei messaggi
    $effect(() => {
        if (!page.params.id && messages.length > 0) {
            sessionStorage.setItem(DRAFT_KEY, JSON.stringify(messages));
        }
    });

    async function sendQuery() {
        if (query.trim() === "") return

        const userQuery = query.trim()
        query = ""

        sequence_number += 1
        messages.push({role: "user", content: userQuery, sequence_number: sequence_number})
        loading = true
        error = null
        saving_conversations_success = null

        try {
            const response = await (debugMode ? askDebug(userQuery) : ask(userQuery))
            sequence_number += 1
            messages.push({
                role: "assistant",
                variant: "answer",
                content: response.answer,
                debug_info: debugMode ? response : null,
                isExpanded: false,
                sequence_number: sequence_number
            })

        } catch (e) {
            error = e.message
            messages.push({
                role: "assistant",
                variant: "error",
                content: "Non sono riuscito a generare una risposta. Riprova tra poco.",
            })
            console.error(e)

        } finally {
            loading = false
        }
    }

    async function saveConversation(){
        if (messages.length === 0) return
        const messagesToSave = messages.filter((message) => message.variant !== "error")

        if (messagesToSave.length === 0) return

        saving_conversations_loading = true
        saving_conversations_error = null
        saving_conversations_success = null

        try {
            await save_conversation(conversation_title, messagesToSave)
            saving_conversations_success = "Conversation saved successfully."
            
            //puliamo il sessionStorage dato che l'abbiamo salvata sul DB
            sessionStorage.removeItem(DRAFT_KEY);
        } catch (e){
            saving_conversations_error = e.message
            console.error(e)
        } finally {
            saving_conversations_loading = false
            toggle()
        }

    }

    async function loadConversation(id){
        loading_conversation = true
        loading_conversation_error = null

        try {
            const conversation = await getConversation(id)
            let loadedMessages = conversation.messages
            loadedMessages.sort((a, b) => a.sequence_number - b.sequence_number)
            messages = loadedMessages

            sequence_number = messages.length > 0 ? Math.max(...messages.map(m => m.sequence_number)) : 0
        } catch (e){
            loading_conversation_error = e.message
            console.error(e)
        } finally {
            loading_conversation = false
        }
    }
</script>

<Modal isOpen={modalOpen} {toggle}>
    <ModalHeader toggle={toggle}>Insert a name for the conversation</ModalHeader>
    <ModalBody>
        <Input bind:value={conversation_title} placeholder="Conversation title" minlength="3" maxlength="50"/>
    </ModalBody>

    <ModalFooter>
        <Button color="primary" onclick={saveConversation} disabled={conversation_title.trim().length < 3 || conversation_title.trim().length > 50 }>Save</Button>
        <Button color="danger" onclick={toggle}>Cancel</Button>
    </ModalFooter>
</Modal>

<section class="chat-page">
    <header class="chat-header">
        <div>
            <p class="eyebrow">Chat</p>
            <h1>Assistente documentale</h1>
        </div>

        <div class="chat-actions">
            {#if isAdmin}
                <div class="d-flex align-items-center mb-1">
                    <Input type="switch" id="debugSwitch" bind:checked={debugMode} label="Debug Mode" />
                </div>
            {/if}

            <div class="thinking-slot">
                {#if loading}
                    <Badge color="secondary" pill>Sto pensando...</Badge>
                {/if}
            </div>

            <Button
                    color="primary"
                    disabled={messages.length === 0 || saving_conversations_loading || loading}
                    onclick={toggle}
            >
                {saving_conversations_loading ? "Saving..." : "Save conversation"}
            </Button>

            <div class="save-feedback" aria-live="polite">
                {#if saving_conversations_success}
                    <span class="save-success">{saving_conversations_success}</span>
                {:else if saving_conversations_error}
                    <span class="save-error">{saving_conversations_error}</span>
                {/if}
            </div>
        </div>
    </header>

    <div class="message-container" bind:this={chatContainer}>
        {#if messages.length === 0}
            <div class="empty-state">
                <h2>Inizia una conversazione</h2>
                <p>Fai qualsiasi domanda riguardante il corso di studi in informatica.</p>
            </div>
        {:else}
            {#each messages as message}
                <article class:user-row={message.role === "user"} class="message-row">
                    <div class:user-avatar={message.role === "user"} class="message-avatar">
                        {message.role === "user" ? "TU" : "AI"}
                    </div>

                    <div class="message-body">
                        <div class:user-meta={message.role === "user"} class="message-meta">
                            <strong>{message.role === "user" ? "Tu" : "Assistente"}</strong>

                            {#if message.variant === "error"}
                                <Badge color="danger" pill>Errore</Badge>
                            {:else if message.role === "assistant"}
                                <Badge color="light" pill>Bot</Badge>
                            {/if}
                        </div>

                        {#if message.variant === "error"}
                            <Alert color="danger" fade={false}>
                                <strong>Errore nella risposta del bot.</strong>
                                <p>{message.content}</p>
                            </Alert>
                        {:else}
                            <div class:user-bubble={message.role === "user"} class="message-bubble">
                                {message.content}

                                {#if message.debug_info}
                                    <div class="mt-3">
                                        <Button color="secondary" size="sm" onclick={() => message.isExpanded = !message.isExpanded}>
                                            {message.isExpanded ? 'Nascondi Debug' : 'Mostra Debug'}
                                        </Button>
                                        <Collapse isOpen={message.isExpanded} class="mt-2">
                                            <div class="p-3 bg-light border rounded text-dark text-start" style="font-size: 0.85rem; max-width: 100%; overflow-x: auto;">
                                                {#if message.debug_info.originalQuery}
                                                    <div><strong>Original Query:</strong> {message.debug_info.originalQuery}</div>
                                                {/if}
                                                {#if message.debug_info.finalQuery}
                                                    <div><strong>Final Query:</strong> {message.debug_info.finalQuery}</div>
                                                {/if}
                                                {#if message.debug_info.retrievedContext && message.debug_info.retrievedContext.length > 0}
                                                    <div class="mt-2"><strong>Retrieved Context:</strong></div>
                                                    <ul class="mb-0 ps-3 mt-1">
                                                        {#each message.debug_info.retrievedContext as context}
                                                            <li class="mb-2">
                                                                <div><strong>Score:</strong> {context.score}</div>
                                                                <div><strong>Text:</strong> <span class="text-muted">{context.text}</span></div>
                                                            </li>
                                                        {/each}
                                                    </ul>
                                                {/if}
                                            </div>
                                        </Collapse>
                                    </div>
                                {/if}
                            </div>
                        {/if}
                    </div>
                </article>
            {/each}
        {/if}
    </div>

    <form
            class="composer"
            onsubmit={(event) => {
            event.preventDefault()
            sendQuery()
        }}
    >
        <div class="composer-input">
            <Input
                    bind:value={query}
                    disabled={loading}
                    placeholder="Scrivi una domanda sui documenti..."
                    type="text"
            />
        </div>

        <Button color="dark" disabled={loading || query.trim() === ""} type="submit">
            {loading ? "Invio..." : "Invia"}
        </Button>
    </form>
</section>

<style>
    .chat-page {
        display: flex;
        height: 100%;
        min-height: 0;
        flex-direction: column;
    }

    .chat-header {
        display: flex;
        flex: 0 0 auto;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .chat-actions {
        display: flex;
        width: 220px;
        flex: 0 0 220px;
        flex-direction: column;
        align-items: flex-end;
        gap: 0.45rem;
    }

    .thinking-slot {
        min-height: 24px;
    }

    .save-feedback {
        min-height: 18px;
        max-width: 220px;
        font-size: 0.78rem;
        line-height: 1.2;
        text-align: right;
    }

    .save-success {
        color: #198754;
    }

    .save-error {
        color: #b42318;
    }

    .eyebrow {
        margin: 0 0 0.35rem;
        color: #6b7280;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    h1 {
        margin: 0;
        color: #111827;
        font-size: 1.65rem;
        font-weight: 750;
    }

    .message-container {
        display: flex;
        min-height: 0;
        flex: 1;
        flex-direction: column;
        gap: 1rem;
        overflow: auto;
        padding-right: 0.25rem;
    }

    .empty-state {
        display: grid;
        height: 100%;
        min-height: 260px;
        place-content: center;
        color: #6b7280;
        text-align: center;
    }

    .empty-state h2 {
        margin: 0 0 0.5rem;
        color: #111827;
        font-size: 1.2rem;
    }

    .empty-state p {
        max-width: 460px;
        margin: 0;
    }

    .message-row {
        display: flex;
        max-width: 82%;
        gap: 0.75rem;
        align-items: flex-start;
    }

    .message-row.user-row {
        align-self: flex-end;
        flex-direction: row-reverse;
    }

    .message-avatar {
        display: grid;
        width: 36px;
        height: 36px;
        place-items: center;
        flex: 0 0 36px;
        color: #ffffff;
        background: #6b7280;
        border-radius: 50%;
        font-size: 0.72rem;
        font-weight: 700;
    }

    .message-avatar.user-avatar {
        background: #111827;
    }

    .message-body {
        min-width: 0;
    }

    .message-meta {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.35rem;
        color: #4b5563;
        font-size: 0.8rem;
    }

    .message-meta.user-meta {
        justify-content: flex-end;
    }

    .message-bubble {
        padding: 0.85rem 1rem;
        color: #1f2937;
        white-space: pre-wrap;
        background: #f3f5f7;
        border: 1px solid #e3e8ef;
        border-radius: 14px;
    }

    .message-bubble.user-bubble {
        color: #ffffff;
        background: #111827;
        border-color: #111827;
    }

    .message-body :global(.alert) {
        margin: 0;
        border-radius: 14px;
    }

    .message-body :global(.alert p) {
        margin: 0.35rem 0 0;
    }

    .message-body :global(.alert small) {
        display: block;
        margin-top: 0.5rem;
        opacity: 0.8;
    }

    .composer {
        display: flex;
        flex: 0 0 auto;
        gap: 0.75rem;
        margin-top: 1.25rem;
        padding-top: 1.25rem;
        border-top: 1px solid #e5e7eb;
    }

    .composer-input {
        flex: 1;
    }
</style>
