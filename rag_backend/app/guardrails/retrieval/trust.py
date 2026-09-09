"""Deterministic document-trust prior.

Kept free of heavy imports so it can be exercised without Qdrant / llama-index:
ASP combines the value produced here with the retrieval score and the chunk
security status to decide whether a chunk is usable.
"""

# Documents served by the institution itself are authoritative for this domain.
INSTITUTIONAL_DOMAIN = "unical.it"

TRUST_INSTITUTIONAL = 100
TRUST_HTTPS = 70
TRUST_OTHER_SOURCE = 55
TRUST_UNSOURCED = 50


def document_trust(metadata: dict) -> int:
    """Map a chunk's provenance to a 0..100 trust score."""
    source_url = str(metadata.get("source_url") or "").strip().lower()
    if source_url in {"", "none", "null"}:
        return TRUST_UNSOURCED
    if INSTITUTIONAL_DOMAIN in source_url:
        return TRUST_INSTITUTIONAL
    if source_url.startswith("https://"):
        return TRUST_HTTPS
    return TRUST_OTHER_SOURCE
