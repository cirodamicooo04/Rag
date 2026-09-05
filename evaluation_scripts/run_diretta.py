"""
Invia le query dei due dataset (attacco diretto + legittime)
all'endpoint /ask del backend, e salva i risultati grezzi in un CSV.

Va eseguito DUE VOLTE, con configurazioni diverse di config.py:

  - Baseline: tutti i flag di sicurezza a False, backend riavviato
    -> python run_diretta.py baseline
    (output: results/risultati_run_A_baseline.csv)

  - Completo: tutti i flag di sicurezza a True, backend riavviato
    -> python run_diretta.py completo
    (output: results/risultati_run_B_completo.csv)

La pausa tra una chiamata e l'altra è più lunga in modalità "completo"
(30s invece di 20s), perché ogni query può attivare fino a 3 chiamate
Groq in sequenza (Intent Classifier, generazione, LLM Judge) anziché
una sola come in Baseline — così si resta con margine sotto il limite
di token/minuto su entrambi i modelli coinvolti.

Supporta l'aggiunta di nuove query al dataset in qualunque momento: al
riavvio, elabora solo gli id non ancora completati con successo (nuovi,
o falliti in precedenza), senza duplicare righe nel file di output —
ogni id compare sempre una sola volta nel CSV finale, e i due output
(baseline/completo) restano su file separati.
"""

import csv
import sys
import time
import requests
from pathlib import Path
from datetime import datetime

# ============ CONFIGURAZIONE  ============
BASE_URL = "http://localhost:8000/api/v1"          # indirizzo del tuo backend
ASK_ENDPOINT = f"{BASE_URL}/ask"
ATTACK_DATASET = "datasets/dataset_attacco_diretto.csv"
LEGIT_DATASET = "datasets/dataset_query_legittime.csv"

MODALITA = {
    "baseline": {
        "output_file": "results/risultati_run_A_baseline.csv",
        "sleep_between_calls": 20,
    },
    "completo": {
        "output_file": "results/risultati_run_B_completo.csv",
        "sleep_between_calls": 30,
    },
}

RETRY_WAIT_ON_ERROR = 75        # secondi di attesa se arriva un 500
MAX_RETRIES = 3                 # tentativi massimi per singola query
REQUEST_TIMEOUT = 60            # timeout HTTP in secondi
# ===================================================================

CAMPI = [
    "gruppo", "id", "question", "answer", "marker_atteso",
    "marker_trovato", "status_code", "durata_sec", "errore",
    "tentativi", "timestamp",
]


def carica_dataset(path):
    """Legge un CSV e restituisce una lista di dizionari."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def invia_query(question: str) -> dict:
    """
    Invia una query all'endpoint /ask, con retry su errore.
    Restituisce un dizionario con risposta, tempo di risposta ed
    eventuale errore.
    """
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

            print(
                f"  [tentativo {tentativo}/{MAX_RETRIES}] "
                f"status {resp.status_code}, attendo {RETRY_WAIT_ON_ERROR}s..."
            )
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
    """Controlla se il marcatore compare nella risposta (case-insensitive)."""
    if not marker:
        return False
    return marker.lower() in (answer or "").lower()


def carica_righe_esistenti(output_path: Path) -> dict:
    """Legge il CSV di output già esistente (se c'è) e restituisce un
    dizionario {id: riga}, così da poter sovrascrivere in modo pulito
    eventuali righe fallite senza mai duplicare un id."""
    if not output_path.exists():
        return {}

    righe = {}
    with open(output_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for riga in reader:
            righe[riga["id"]] = riga
    return righe


def salva_tutte_le_righe(output_path: Path, righe: dict):
    """Riscrive l'intero file di output a partire dal dizionario
    {id: riga}, garantendo che ogni id compaia una sola volta."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPI, delimiter=";")
        writer.writeheader()
        for riga in righe.values():
            writer.writerow(riga)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in MODALITA:
        print("Uso: python run_diretta.py <baseline|completo>")
        sys.exit(1)

    modalita = sys.argv[1]
    output_file = MODALITA[modalita]["output_file"]
    sleep_between_calls = MODALITA[modalita]["sleep_between_calls"]

    print(f"Modalità: {modalita}")
    print(f"Ricorda: config.py deve avere tutti i flag di sicurezza a "
          f"{'False' if modalita == 'baseline' else 'True'}, backend riavviato.\n")

    attacchi = carica_dataset(ATTACK_DATASET)
    legittime = carica_dataset(LEGIT_DATASET)

    output_path = Path(output_file)
    righe_esistenti = carica_righe_esistenti(output_path)

    completati = {
        id_ for id_, riga in righe_esistenti.items()
        if riga.get("status_code") == "200"
    }

    if completati:
        print(f"Trovate {len(completati)} query già completate con successo, verranno saltate.")

    da_processare_attacchi = [r for r in attacchi if r["id"] not in completati]
    da_processare_legittime = [r for r in legittime if r["id"] not in completati]

    print(f"Da processare: {len(da_processare_attacchi)} query di attacco e {len(da_processare_legittime)} legittime.")
    print(f"Output: {output_file}\n")

    totale = len(da_processare_attacchi) + len(da_processare_legittime)
    contatore = 0

    for riga in da_processare_attacchi:
        contatore += 1
        print(f"[{contatore}/{totale}] Attacco {riga['id']}...")
        risultato = invia_query(riga["query"])
        trovato = marcatore_presente(risultato["answer"], riga["marker"])

        righe_esistenti[riga["id"]] = {
            "gruppo": "attacco",
            "id": riga["id"],
            "question": riga["query"],
            "answer": risultato["answer"],
            "marker_atteso": riga["marker"],
            "marker_trovato": trovato,
            "status_code": risultato["status_code"],
            "durata_sec": risultato["durata_sec"],
            "errore": risultato["errore"],
            "tentativi": risultato["tentativi"],
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        salva_tutte_le_righe(output_path, righe_esistenti)
        print(f"  -> marker trovato: {trovato}")
        time.sleep(sleep_between_calls)

    for riga in da_processare_legittime:
        contatore += 1
        print(f"[{contatore}/{totale}] Legittima {riga['id']}...")
        risultato = invia_query(riga["query"])

        righe_esistenti[riga["id"]] = {
            "gruppo": "legittima",
            "id": riga["id"],
            "question": riga["query"],
            "answer": risultato["answer"],
            "marker_atteso": "",
            "marker_trovato": "",
            "status_code": risultato["status_code"],
            "durata_sec": risultato["durata_sec"],
            "errore": risultato["errore"],
            "tentativi": risultato["tentativi"],
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        salva_tutte_le_righe(output_path, righe_esistenti)
        time.sleep(sleep_between_calls)

    print(f"\nCompletato. Risultati salvati in {output_file}")


if __name__ == "__main__":
    main()
