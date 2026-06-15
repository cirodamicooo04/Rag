import {apiFetch} from "$lib/api/client.js";

export function getDocuments(){
    return apiFetch("/admin/docs", {
        auth: "required"
    })
}

export function deleteDocument(document_id){
    return apiFetch(`/admin/docs/${document_id}`, {
        auth: "required",
        method: "DELETE"
    })
}

export function approveDocument(document_id){
    return apiFetch(`/admin/docs/${document_id}/approve`, {
        auth: "required",
        method: "POST"
    })
}
