import {apiFetch} from "$lib/api/client.js";

export function save_conversation(conversation_title,messages){
    return apiFetch("/conversations", {
        auth: "required",
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            conversation_title,
            messages: messages
        })
    })
}

export function getSavedConversations(){
    return apiFetch("/conversations", {
        auth: "required"
    })
}

export function getConversation(conversation_id){
    return apiFetch(`/conversations/${conversation_id}`, {
        auth: "required"
    })
}

export function deleteConversation(conversation_id){
    return apiFetch(`/conversations/${conversation_id}`, {
        auth: "required",
        method: "DELETE"
        })
}
