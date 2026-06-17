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

export function getSecurityStatus(document_id){
    return apiFetch(`/admin/docs/${document_id}/security-summary`, {
        auth: "required"
    })
}

export function deleteDataset(){
    return apiFetch("/admin/reset-dataset", {
        auth: "required",
        method: "POST"
    })
}

export function approveChunk(chunk_id){
    return apiFetch(`/admin/chunks/${chunk_id}/approve`, {
        auth: "required",
        method: "POST"
    })
}

export function deleteChunk(chunk_id){
    return apiFetch(`/admin/chunks/${chunk_id}`, {
        auth: "required",
        method: "DELETE"
    })
}

export function uploadDocument(file){
    return apiFetch("/admin/upload-and-process", {
        auth: "required",
        method: "POST",
        body: file
    })
}
