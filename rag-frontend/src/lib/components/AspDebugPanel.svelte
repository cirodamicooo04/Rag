<script>
    import {Badge} from "@sveltestrap/sveltestrap"

    let {title, record} = $props()

    const decisionColor = (value) => {
        if (["allow", "allow_general_chat", "allow_privileged_debug", "retrieve", "generate"].includes(value)) return "success"
        if (value === "block") return "danger"
        if (["human_review", "ask_clarification", "retrieve_again", "regenerate", "return_insufficient_context"].includes(value)) return "warning"
        return "secondary"
    }
</script>

{#if record}
    <div class="asp-card">
        <div class="asp-head">
            <strong>{title}</strong>
            {#if record.action}
                <Badge color={decisionColor(record.action)} pill>{record.action}</Badge>
            {/if}
            {#each (record.flags || []) as flag}
                <Badge color="info" pill>{flag}</Badge>
            {/each}
        </div>

        <div class="asp-grid">
            <span class="asp-label">Azione selezionata</span>
            <span><Badge color={decisionColor(record.action)}>{record.action ?? "—"}</Badge></span>

            {#if record.reasons?.length}
                <span class="asp-label">Motivazioni</span>
                <span>{record.reasons.join(", ")}</span>
            {/if}
            {#if record.selected_items?.length}
                <span class="asp-label">Elementi selezionati</span>
                <span>{record.selected_items.join(", ")}</span>
            {/if}
            {#if record.optimization_cost?.length}
                <span class="asp-label">Costo ottimizzazione</span>
                <span>{record.optimization_cost.join(", ")}</span>
            {/if}
            {#if record.context_consistency}
                <span class="asp-label">Coerenza del contesto</span>
                <span>
                    <Badge color={record.context_consistency.status === "contradictory" ? "danger" : (record.context_consistency.status === "unknown" ? "warning" : "info")}>
                        {record.context_consistency.status}
                    </Badge>
                    ({Math.round((record.context_consistency.confidence || 0) * 100)}%)
                    {record.context_consistency.reason ? ` — ${record.context_consistency.reason}` : ""}
                </span>
            {/if}
        </div>

        {#if record.facts?.length}
            <div class="asp-facts">
                <span class="asp-label">Fatti ASP</span>
                <pre>{record.facts.join("\n")}</pre>
            </div>
        {/if}

        {#if record.error}
            <div class="asp-error">⚠ {record.error}</div>
        {:else if record.satisfiable === false}
            <div class="asp-error">⚠ programma ASP insoddisfacibile</div>
        {/if}
    </div>
{/if}

<style>
    .asp-card { margin-top: .6rem; padding: .6rem .75rem; background: #fff; border: 1px solid #dbe2ea; border-radius: 10px; }
    .asp-head { display: flex; align-items: center; flex-wrap: wrap; gap: .4rem; margin-bottom: .5rem; }
    .asp-grid { display: grid; grid-template-columns: auto 1fr; gap: .3rem .75rem; align-items: center; }
    .asp-label { color: #6b7280; font-weight: 600; font-size: .78rem; }
    .asp-facts { margin-top: .5rem; }
    .asp-facts pre { margin: .2rem 0 0; padding: .5rem; background: #0f172a; color: #e2e8f0; border-radius: 8px; font-size: .75rem; white-space: pre-wrap; word-break: break-word; }
    .asp-error { margin-top: .5rem; color: #b42318; font-size: .8rem; }
</style>
