"""
Fase 1 — carica i 20 documenti di attacco indiretto tramite l'endpoint
/admin/upload-and-process, attende il completamento della pipeline
asincrona interrogando /admin/docs, e registra l'esito (stato finale,
numero di chunk totali/indicizzati/quarantenati) in un CSV.

Gestione della scadenza del token: il token admin viene letto da un
file esterno (ADMIN_TOKEN_FILE) a ogni richiesta, non incollato nello
script. Se il token scade (errore 401), lo script si mette in pausa e
chiede di aggiornare il file, poi riprende da dove si era fermato —
non serve riavviare l'intero processo.

Prerequisiti:
- config.py del backend con DOCUMENT_CLASSIFIER=True
- backend riavviato dopo la modifica
- un file di testo ADMIN_TOKEN_FILE contenente solo il token admin
  (senza "Bearer ", solo il token)
- i 20 file .txt nella cartella DOCS_FOLDER

Uso:
    python fase1_quarantena.py
"""

import csv
import time
import requests
from pathlib import Path

# ============ CONFIGURAZIONE ============
BASE_URL = "http://localhost:8000/api/v1"
DOCS_FOLDER = "documenti_attacco"       # cartella con i 20 .txt
OUTPUT_FILE = "results/risultati_fase1_quarantena.csv"
ADMIN_TOKEN_FILE = "admin_token.txt"    # file con solo il token, una riga

POLL_INTERVAL = 5          # secondi tra un controllo di stato e l'altro
POLL_TIMEOUT = 120         # secondi massimi di attesa per documento
SLEEP_BETWEEN_UPLOADS = 30  # secondi tra un caricamento e l'altro
# ===================================================================

STATI_TERMINALI = {"INDEXED", "PARTIALLY_INDEXED", "REJECTED_SECURITY", "ERROR"}


def leggi_token() -> str:
    """Legge il token admin dal file, ogni volta (così un aggiornamento
    del file si riflette subito senza riavviare lo script)."""
    path = Path(ADMIN_TOKEN_FILE)
    if not path.exists():
        raise FileNotFoundError(
            f"File del token non trovato: {ADMIN_TOKEN_FILE}. "
            f"Crealo con dentro solo il token admin (senza 'Bearer ')."
        )
    return path.read_text(encoding="utf-8").strip()


def headers_correnti() -> dict:
    return {"Authorization": f"Bearer {leggi_token()}"}


def richiesta_con_retry_su_401(metodo, url, **kwargs):
    """Esegue una richiesta HTTP; se riceve 401 (token scaduto), si
    ferma, chiede di aggiornare il file del token, e riprova."""
    while True:
        kwargs["headers"] = headers_correnti()
        resp = requests.request(metodo, url, **kwargs)

        if resp.status_code == 401:
            print(f"\n⚠️  Token scaduto (401) su {url}")
            input(
                f"    Aggiorna il contenuto di '{ADMIN_TOKEN_FILE}' con un "
                f"token fresco, poi premi INVIO per riprovare..."
            )
            continue

        return resp


def carica_documento(path: Path) -> dict:
    """Carica un documento tramite /admin/upload-and-process.
    Restituisce il DTO del documento (con fileHash) o solleva
    un'eccezione in caso di errore HTTP diverso da 401."""
    with open(path, "rb") as f:
        files = {"file": (path.name, f, "text/plain")}
        resp = richiesta_con_retry_su_401(
            "POST",
            f"{BASE_URL}/admin/upload-and-process",
            files=files,
            timeout=30,
        )
    resp.raise_for_status()
    return resp.json()


def attendi_completamento(file_hash: str) -> dict:
    """Interroga /admin/docs finché lo stato del documento non è
    terminale, o scade il timeout. Restituisce l'ultimo DTO ottenuto."""
    inizio = time.monotonic()
    ultimo_dto = None

    while time.monotonic() - inizio < POLL_TIMEOUT:
        resp = richiesta_con_retry_su_401(
            "GET",
            f"{BASE_URL}/admin/docs",
            params={"hashes": [file_hash]},
            timeout=15,
        )
        resp.raise_for_status()
        risultati = resp.json()

        if risultati:
            ultimo_dto = risultati[0]
            if ultimo_dto["status"] in STATI_TERMINALI:
                return ultimo_dto

        time.sleep(POLL_INTERVAL)

    return ultimo_dto or {}


def main():
    cartella = Path(DOCS_FOLDER)
    file_documenti = sorted(cartella.glob("*.txt"))

    if not file_documenti:
        print(f"Nessun file .txt trovato in {DOCS_FOLDER}")
        return

    print(f"Trovati {len(file_documenti)} documenti da caricare.\n")

    campi = [
        "documento", "file_hash", "status_finale",
        "total_chunks", "indexed_chunks", "quarantined_chunks",
        "quarantenato",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campi, delimiter=";")
        writer.writeheader()

        for i, path in enumerate(file_documenti, start=1):
            print(f"[{i}/{len(file_documenti)}] Carico {path.name}...")

            try:
                dto_upload = carica_documento(path)
            except requests.exceptions.HTTPError as e:
                print(f"  Errore nel caricamento: {e}")
                writer.writerow({
                    "documento": path.name,
                    "file_hash": "",
                    "status_finale": "ERRORE_UPLOAD",
                    "total_chunks": "",
                    "indexed_chunks": "",
                    "quarantined_chunks": "",
                    "quarantenato": "",
                })
                f.flush()
                continue

            file_hash = dto_upload["fileHash"]
            print(f"  Caricato, hash={file_hash[:12]}... attendo elaborazione...")

            dto_finale = attendi_completamento(file_hash)
            status = dto_finale.get("status", "TIMEOUT")
            total = dto_finale.get("totalChunks", "")
            indexed = dto_finale.get("indexedChunks", "")
            quarantined = dto_finale.get("quarantinedChunks", "")

            # "Quarantenato" = almeno un chunk è stato messo in quarantena
            quarantenato = isinstance(quarantined, int) and quarantined > 0

            print(f"  Stato finale: {status} (totali={total}, indicizzati={indexed}, quarantena={quarantined})")

            writer.writerow({
                "documento": path.name,
                "file_hash": file_hash,
                "status_finale": status,
                "total_chunks": total,
                "indexed_chunks": indexed,
                "quarantined_chunks": quarantined,
                "quarantenato": quarantenato,
            })
            f.flush()

            time.sleep(SLEEP_BETWEEN_UPLOADS)

    print(f"\nCompletato. Risultati salvati in {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
