import {apiFetch} from "$lib/api/client.js";

export function getLogs(){
    return apiFetch("/admin/logs", {
        auth: "required"
    })
}

export function clearLogs(){
    return apiFetch("/admin/logs", {
        auth: "required",
        method: "DELETE"
    })
}

export function deleteLog(log_id){
    return apiFetch(`/admin/logs/${log_id}`, {
        auth: "required",
        method: "DELETE"
    })
}