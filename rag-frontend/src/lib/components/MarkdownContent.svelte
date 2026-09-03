<script>
    import {marked} from "marked"
    import DOMPurify from "dompurify"

    let {content = ""} = $props()

    marked.setOptions({gfm: true, breaks: true})

    let html = $derived(DOMPurify.sanitize(marked.parse(content ?? "")))
</script>

<div class="markdown-content">
    {@html html}
</div>

<style>
    .markdown-content {
        white-space: normal;
        overflow-wrap: break-word;
    }

    .markdown-content :global(p) {
        margin: 0 0 0.75rem;
    }

    .markdown-content :global(p:last-child) {
        margin-bottom: 0;
    }

    .markdown-content :global(ul),
    .markdown-content :global(ol) {
        margin: 0 0 0.75rem;
        padding-left: 1.4rem;
    }

    .markdown-content :global(li) {
        margin-bottom: 0.25rem;
    }

    .markdown-content :global(strong) {
        font-weight: 600;
    }

    .markdown-content :global(a) {
        color: inherit;
        text-decoration: underline;
    }

    .markdown-content :global(code) {
        background: rgba(0, 0, 0, 0.06);
        border-radius: 4px;
        padding: 0.1rem 0.35rem;
        font-size: 0.9em;
    }

    .markdown-content :global(pre) {
        background: rgba(0, 0, 0, 0.06);
        border-radius: 8px;
        padding: 0.75rem;
        overflow-x: auto;
        margin: 0 0 0.75rem;
    }

    .markdown-content :global(pre code) {
        background: none;
        padding: 0;
    }

    .markdown-content :global(blockquote) {
        margin: 0 0 0.75rem;
        padding-left: 0.85rem;
        border-left: 3px solid rgba(0, 0, 0, 0.15);
        color: inherit;
        opacity: 0.85;
    }

    .markdown-content :global(hr) {
        margin: 0.85rem 0;
        border: none;
        border-top: 1px solid rgba(0, 0, 0, 0.12);
    }

    .markdown-content :global(h1),
    .markdown-content :global(h2),
    .markdown-content :global(h3),
    .markdown-content :global(h4) {
        margin: 0.9rem 0 0.5rem;
        font-weight: 600;
        line-height: 1.3;
    }

    .markdown-content :global(h1:first-child),
    .markdown-content :global(h2:first-child),
    .markdown-content :global(h3:first-child),
    .markdown-content :global(h4:first-child) {
        margin-top: 0;
    }

    .markdown-content :global(table) {
        display: block;
        overflow-x: auto;
        border-collapse: collapse;
        width: 100%;
        margin: 0 0 0.75rem;
        font-size: 0.92em;
    }

    .markdown-content :global(th),
    .markdown-content :global(td) {
        border: 1px solid rgba(0, 0, 0, 0.15);
        padding: 0.4rem 0.6rem;
        text-align: left;
        vertical-align: top;
    }

    .markdown-content :global(th) {
        background: rgba(0, 0, 0, 0.05);
        font-weight: 600;
    }
</style>
