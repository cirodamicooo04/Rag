import {apiFetch} from "$lib/api/client.js";

export function getDocuments(){
    return apiFetch("/admin/docs", {
        auth: "required"
    })
}
