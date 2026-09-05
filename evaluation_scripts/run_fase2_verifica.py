"""
Invia le 20 query di verifica all'endpoint /ask e controlla se il
marcatore del documento corrispondente compare nella risposta.

Da lanciare DUE VOLTE, con configurazioni diverse di config.py:
  - Fase 2a: Input/Output Guardrail disattivati (NORMALIZATION_QUERY,
    LLM_GUARD_CONTROL, INTENT_CLASSIFIER_CONTROL, LLM_JUDGE_CONTROL
    tutti False) -> python run_fase2_verifica.py fase2a
  - Fase 2b: tutti i flag di sicurezza attivi (True), ad eccezione del
    fatto che i documenti sono stati approvati manualmente in Fase 2
    -> python run_fase2_verifica.py fase2b

Prerequisito: i 20 documenti devono essere già stati approvati prima di lanciare questo script.

Uso:
    python run_fase2_verifica.py <nome_fase>
"""

import csv
import sys
import time
import requests
from pathlib import Path
from datetime import datetime

# ============ CONFIGURAZIONE ============
BASE_URL = "http://localhost:8000/api/v1"
ASK_ENDPOINT = f"{BASE_URL}/ask"
VERIFICA_DATASET = "datasets/dataset_query_verifica.csv"

SLEEP_BETWEEN_CALLS = 25   # più prudente della Baseline, dato che in
                           # Fase 2b ogni query può attivare più modelli
RETRY_WAIT_ON_ERROR = 75
MAX_RETRIES = 3
REQUEST_TIMEOUT = 60
# =========================================


def carica_dataset(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def invia_query(question: str) -> dict:
    for tentativo in range(1, MAX_RETRIES + 1):
        inizio = time.monotonic()
        try:
            resp = requests.post(
                ASK_ENDPOINT,
                json={"question": question},
                timeout=REQUEST_TIMEOUT,
            )
            durata = time.monotonic() - inizio

            if resp.status_code == 200:
                answer = resp.json().get("answer", "")
                return {
                    "status_code": 200,
                    "answer": answer,
                    "durata_sec": round(durata, 2),
                    "errore": "",
                    "tentativi": tentativo,
                }

            print(f"  [tentativo {tentativo}/{MAX_RETRIES}] status {resp.status_code}, attendo {RETRY_WAIT_ON_ERROR}s...")
            if tentativo < MAX_RETRIES:
                time.sleep(RETRY_WAIT_ON_ERROR)

        except requests.exceptions.RequestException as e:
            print(f"  [tentativo {tentativo}/{MAX_RETRIES}] errore di rete: {e}")
            if tentativo < MAX_RETRIES:
                time.sleep(RETRY_WAIT_ON_ERROR)

    return {
        "status_code": None,
        "answer": "",
        "durata_sec": None,
        "errore": "Falliti tutti i tentativi",
        "tentativi": MAX_RETRIES,
    }


def marcatore_presente(answer: str, marker: str) -> bool:
    if not marker:
        return False
    return marker.lower() in (answer or "").lower()


def carica_gia_completati(output_path: Path) -> set:
    if not output_path.exists():
        return set()
    completati = set()
    with open(output_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for riga in reader:
            if riga.get("status_code") == "200":
                completati.add(riga["id"])
    return completati


def main():
    if len(sys.argv) != 2:
        print("Uso: python run_fase2_verifica.py <fase2a|fase2b>")
        sys.exit(1)

    nome_fase = sys.argv[1]
    output_file = f"risultati_{nome_fase}_verifica.csv"

    verifica = carica_dataset(VERIFICA_DATASET)

    output_path = Path(output_file)
    gia_completati = carica_gia_completati(output_path)
    if gia_completati:
        print(f"Trovate {len(gia_completati)} query già completate, verranno saltate.")
    verifica = [r for r in verifica if r["id"] not in gia_completati]

    print(f"Fase: {nome_fase}")
    print(f"Da processare: {len(verifica)} query di verifica.")
    print(f"Output: {output_file}\n")

    campi = [
        "id", "documento", "question", "answer", "marker_atteso",
        "marker_trovato", "status_code", "durata_sec", "errore",
        "tentativi", "timestamp",
    ]

    scrivi_intestazione = not output_path.exists()

    with open(output_path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campi, delimiter=";")
        if scrivi_intestazione:
            writer.writeheader()

        for i, riga in enumerate(verifica, start=1):
            print(f"[{i}/{len(verifica)}] {riga['id']} ({riga['documento']})...")
            risultato = invia_query(riga["query"])
            trovato = marcatore_presente(risultato["answer"], riga["marker"])

            writer.writerow({
                "id": riga["id"],
                "documento": riga["documento"],
                "question": riga["query"],
                "answer": risultato["answer"],
                "marker_atteso": riga["marker"],
                "marker_trovato": trovato,
                "status_code": risultato["status_code"],
                "durata_sec": risultato["durata_sec"],
                "errore": risultato["errore"],
                "tentativi": risultato["tentativi"],
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            })
            f.flush()
            print(f"  -> marker trovato: {trovato}")
            time.sleep(SLEEP_BETWEEN_CALLS)

    print(f"\nCompletato. Risultati salvati in {output_file}")


if __name__ == "__main__":
    main()
