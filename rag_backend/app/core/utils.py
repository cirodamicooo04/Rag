import hashlib
from pathlib import Path

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


#L'id deterministico serve per evitare che due file con lo stesso contenuto vengano raggruppati in chunk diversi o indicizzati nuovamente
def deterministic_chunk_id(file_hash: str, page: int, chunk_index: int) -> str:
    raw = f"{file_hash}_{page}_{chunk_index}"
    return hashlib.sha256(raw.encode()).hexdigest()