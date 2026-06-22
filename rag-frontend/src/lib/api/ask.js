import {apiFetch} from "$lib/api/client.js";

export function ask(question) {
    return apiFetch("/ask", {
        auth: "optional",
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question} )
    })
}

export function askDebug(question) {
    return apiFetch("/admin/ask-debug", {
        auth: "required",
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question} )
    })
}
