<script>
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import { Alert, ListGroup, Spinner } from "@sveltestrap/sveltestrap";
    import {getSavedConversations, deleteConversation} from "$lib/api/conversation.js";
    import ConversationListItem from "$lib/components/ConversationListItem.svelte";

    let saved_conversations = $state([]);
    let loading = $state(false)
    let savedConversationError = $state(null)
    let deleteConversationError = $state(null)

    onMount(async () => {
        loading = true
        savedConversationError = null
        try {
            saved_conversations = await getSavedConversations()
        } catch (e) {
            console.error(e)
            savedConversationError = e
        } finally {
            loading = false
        }
    })

    async function deleteConv(id) {
        loading = true
        deleteConversationError = null

        try {
            await deleteConversation(id)
            saved_conversations = saved_conversations.filter(conv => conv.id !== id)
        } catch (e) {
            console.error(e)
            deleteConversationError = e
        } finally {
            loading = false
        }
    }
</script>

<section class="saved-conversations-page">
    <header class="saved-conversations-header">
        <h1>Saved Conversations</h1>
    </header>

    {#if loading}
        <div class="loading-state">
            <Spinner size="sm" />
            <span>Loading...</span>
        </div>
    {/if}

    {#if savedConversationError}
        <Alert color="danger" fade={false}>
            Failed to load saved conversations. Please try again.
        </Alert>
    {/if}

    {#if deleteConversationError}
        <Alert color="danger" fade={false}>
            Failed to delete conversation. Please try again.
        </Alert>
    {/if}

    {#if saved_conversations.length === 0 && !loading && !savedConversationError}
        <p class="empty-state">No saved conversations found.</p>
    {/if}

    {#if saved_conversations.length > 0}
        <div class="saved-conversations-list-container">
            <ListGroup class="saved-conversations-list">
                {#each saved_conversations as conversation (conversation.id)}
                    <ConversationListItem
                        {conversation}
                        disabled={loading}
                        onDelete={() => deleteConv(conversation.id)}
                        onOpen={() => goto(`/app/${conversation.id}`)}
                    />
                {/each}
            </ListGroup>
        </div>
    {/if}

</section>

<style>
    .saved-conversations-page {
        display: flex;
        height: 100%;
        min-height: 0;
        flex-direction: column;
    }

    .saved-conversations-header {
        flex: 0 0 auto;
        margin-bottom: 1rem;
    }

    .saved-conversations-header h1 {
        margin: 0;
        color: #111827;
        font-size: 1.65rem;
        font-weight: 750;
    }

    .loading-state {
        display: flex;
        flex: 0 0 auto;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        color: #6b7280;
        font-size: 0.9rem;
    }

    .empty-state {
        margin: 0;
        color: #6b7280;
    }

    .saved-conversations-list-container {
        min-height: 0;
        flex: 1;
        overflow-y: auto;
        padding-right: 0.25rem;
    }

    :global(.saved-conversations-list) {
        margin: 0;
    }
</style>
