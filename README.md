# RAG Backend - Sistema di Retrieval-Augmented Generation Sicuro

Questo progetto implementa un sistema RAG (Retrieval-Augmented Generation) avanzato, incentrato sulla sicurezza. Utilizza una pipeline di ingestion e un'interfaccia di chat dotate di diversi "guardrail" (barriere di sicurezza) per analizzare intenti, neutralizzare attacchi (Prompt Injection) e validare i documenti caricati.

Al momento, il sistema supporta esclusivamente l'upload di file di testo in formato `.txt`.

Il repository contiene due varianti:
- **Variante base** (branch `main`): i guardrail sono orchestrati da una cascata di controlli in Python. Si avvia interamente con Docker Compose (vedi [sezione 3](#3-avvio-della-variante-base-branch-main)).
- **Variante ASP** (branch `asp`): alla cascata di guardrail si affianca un *control plane* basato su Answer Set Programming (solver `clingo`) che decide le azioni della pipeline RAG. Il backend va avviato manualmente (vedi [sezione 4](#4-avvio-della-variante-asp-branch-asp)).

## Architettura e Tecnologie
- **Backend**: FastAPI (Python)
- **Modelli LLM**: Groq (per un'esecuzione ultra-rapida in cloud tramite API compatibili con OpenAI)
- **Modelli Locali**: Hugging Face (embedding con `intfloat/multilingual-e5-base` e prompt injection detection con `meta-llama/Llama-Prompt-Guard-2-86M`)
- **Database Vettoriale**: Qdrant
- **Database applicativo**: SQLite (documenti, conversazioni, log)
- **Autenticazione**: Keycloak (supportato da PostgreSQL)
- **Frontend**: SvelteKit (nella cartella `rag-frontend`)
- **Policy engine (solo variante ASP)**: `clingo` (Answer Set Programming)

---

## 1. Requisiti Preliminari

1. **Docker** installato sul sistema.
2. **Node.js**, necessario per avviare l'interfaccia frontend SvelteKit in locale.
3. **Python 3.12**, necessario solo per la variante ASP (backend avviato fuori da Docker).
4. **Chiave API di Groq** (**obbligatoria**):
   - Vai su [Groq Console](https://console.groq.com/keys) e crea una API Key gratuita.
5. **Token di Hugging Face (HF_TOKEN)** (**obbligatorio**):
   - Il progetto utilizza il modello di sicurezza `meta-llama/Llama-Prompt-Guard-2-86M`. Poiché è un modello con restrizioni, **devi prima accettare i termini di utilizzo** sulla pagina ufficiale.
   - Vai su: [meta-llama/Llama-Prompt-Guard-2-86M su Hugging Face](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M) e clicca su "Agree" o "Acknowledge license".
   - Genera un token di accesso (Read) dalle tue [Impostazioni di Hugging Face](https://huggingface.co/settings/tokens).

> ⚠️ **Llama Prompt Guard è fail-closed.** Se il modello non può essere caricato (token mancante o non valido, termini non accettati, download fallito) il backend si avvia comunque, ma **ogni query viene considerata non sicura e bloccata**. Se tutte le domande in chat vengono rifiutate, controlla per prima cosa i log del backend alla ricerca del messaggio `Failed to load Llama Guard model`.

---

## 2. Configurazione

1. Clona il repository e spostati nella cartella principale (dove si trova il file `docker-compose.yml`).
2. Crea un file chiamato `.env` copiando il modello `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Apri il file `.env` e inserisci le tue credenziali:
   - Compila `GROQ_API_KEY` con la chiave generata.
   - Compila `HF_TOKEN` con il token di Hugging Face (assicurandoti di aver prima accettato i termini del modello Llama-Prompt-Guard-2-86M, altrimenti il modello non verrà scaricato e, per il comportamento fail-closed, tutte le query verranno bloccate).
   - *Nota: le credenziali di default per Keycloak e Postgres sono già impostate nel file di esempio.*

Lo stesso file `.env` nella root viene letto sia da Docker Compose sia dal backend quando è avviato manualmente.

### Flag dei guardrail
I singoli livelli di difesa si attivano/disattivano da [rag_backend/app/core/config.py](rag_backend/app/core/config.py) (sezione `DEFENSE LAYERS`): `NORMALIZATION_QUERY`, `LLM_GUARD_CONTROL`, `INTENT_CLASSIFIER_CONTROL`, `NORMALIZATION_DOCUMENT`, `DOCUMENT_CLASSIFIER`, `LLM_JUDGE_CONTROL`, ecc. Dopo ogni modifica il backend va riavviato (con Docker è necessario anche ricostruire l'immagine: `docker compose up -d --build backend`).

Comportamenti rilevanti dei guardrail di input:
- **Llama Prompt Guard**: fail-closed (vedi sopra).
- **Intent Classifier**: se l'intento della query non viene riconosciuto, la query viene **bloccata**.

---

## 3. Avvio della Variante Base (branch `main`)

Tutta l'infrastruttura (Backend FastAPI, Qdrant, Keycloak e PostgreSQL) è containerizzata con Docker.

```bash
git checkout main
docker compose up -d --build
```

- Il **Backend (FastAPI)** sarà disponibile su: `http://localhost:8000`
- La **Documentazione API (Swagger)** sarà su: `http://localhost:8000/docs`
- **Keycloak** (Pannello Admin) sarà su: `http://localhost:8089` (user: `admin`, pass: `admin`)
- **Qdrant** sarà in ascolto sulla porta `6333` e `6334`.

*Nota: Al primissimo avvio, il backend scaricherà i modelli di embedding e Llama Prompt Guard da Hugging Face. Potrebbe volerci qualche minuto in base alla tua connessione. La cartella `/rag_backend/data` contenente il database SQLite verrà creata automaticamente.*

Prosegui poi con l'[avvio del frontend](#5-avvio-del-frontend).

---

## 4. Avvio della Variante ASP (branch `asp`)

La variante ASP non ha il backend containerizzato: con Docker vanno avviati solo i servizi di supporto (Qdrant, PostgreSQL e Keycloak), mentre il backend FastAPI va avviato manualmente sulla macchina host e si collega ai servizi su `localhost`.

1. Spostati sul branch della variante:
   ```bash
   git checkout asp
   ```
2. Avvia **solo** Qdrant, PostgreSQL e Keycloak (escludendo il servizio `backend`):
   ```bash
   docker compose up -d qdrant postgres keycloak
   ```
   > Se in precedenza avevi avviato la variante base, ferma il container del backend per liberare la porta `8000`: `docker compose stop backend`.
3. Crea un ambiente virtuale Python e installa le dipendenze (tra cui `clingo`):
   ```bash
   cd rag_backend
   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cpu
   pip install -r requirements.txt
   ```
4. Avvia il backend FastAPI (sempre da `rag_backend`, con il virtualenv attivo):
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   Il backend sarà disponibile su `http://localhost:8000` (Swagger su `http://localhost:8000/docs`). I file SQLite (`rag_backend/data`), i documenti caricati (`rag_backend/docs`) e i log ASP (`rag_backend/logs`) vengono creati in locale.
5. Prosegui con l'[avvio del frontend](#5-avvio-del-frontend).

### Control plane ASP
Le policy ASP si trovano in `rag_backend/app/guardrails/asp/` e coprono le tre fasi della pipeline:
- `input_orchestration.lp`: decide se accettare, bloccare, chiedere chiarimenti o inviare a revisione la query;
- `retrieval_orchestration.lp`: valuta i chunk recuperati (score, trust del documento, coerenza del contesto) e decide se generare, ripetere il retrieval o restituire contesto insufficiente;
- `output_orchestration.lp`: decide se restituire la risposta, rigenerarla o bloccarla.

La fase di retrieval include anche il nuovo controllo di **coerenza del contesto** (`CONTEXT_CONSISTENCY_CONTROL`), che usa un LLM Groq per individuare chunk contraddittori.

Variabili d'ambiente specifiche (da aggiungere al `.env` o da esportare prima di lanciare `uvicorn`):

| Variabile | Default | Descrizione |
|---|---|---|
| `ASP_MODE` | `orchestrator` | `orchestrator`: ASP sceglie l'azione successiva e Python la esegue. `veto`: decide la cascata Python e ASP può solo declassare l'esito a `block` / `human_review`. |
| `CONTEXT_CONSISTENCY_CONTROL` | `true` | Attiva/disattiva il controllo di coerenza del contesto recuperato. |

Le soglie del control plane (`ASP_RAG_CONFIDENCE_THRESHOLD`, `ASP_MIN_RETRIEVAL_SCORE`, `ASP_MAX_RETRIEVAL_ATTEMPTS`, ecc.) sono definite in `config.py`, sezione `ASP CONTROL PLANE`.

**Fallback sicuro**: se `clingo` non è installato o la risoluzione fallisce, il control plane applica l'azione più conservativa per ogni fase (`block` per input e output, `return_insufficient_context` per il retrieval).

**Osservabilità**: ogni decisione ASP (fatti, azione, motivazioni, costo di ottimizzazione) viene registrata in `rag_backend/logs/asp_orchestration.jsonl`. Nel frontend, usando la modalità debug da utente `admin` (endpoint `/api/v1/admin/ask-debug`), il pannello **"ASP control plane"** mostra la decisione presa in ciascuna fase (Input, Retrieval, Output).

---

## 5. Avvio del Frontend

Il frontend è sviluppato in SvelteKit e comunica con il backend e con Keycloak. La procedura è la stessa per entrambe le varianti.

1. Spostati nella cartella del frontend:
   ```bash
   cd rag-frontend
   ```
2. Installa le dipendenze:
   ```bash
   npm install
   ```
3. Avvia il server di sviluppo:
   ```bash
   npm run dev
   ```
4. L'interfaccia utente sarà accessibile all'indirizzo mostrato nel terminale (default `http://localhost:5173`).

---

## 6. Utilizzo

### Utenti Preconfigurati
Il sistema importa automaticamente una configurazione base per Keycloak contenente due utenti già pronti per testare l'applicazione:
- **Amministratore**: Username: `admin` | Password: `admin` (ha accesso alla dashboard per gestire i documenti, per visualizzare i logs e alla modalità debug della chat)
- **Utente Base**: Username: `user` | Password: `user` (può solo chattare)

### Flusso dell'Applicazione
- **Gestione Documenti**: Dall'interfaccia (loggandoti come `admin`), l'amministratore può caricare documenti. Il sistema accetta **solo file .txt**. Una volta caricato, il documento passa attraverso una pipeline che lo pulisce, lo divide in "chunk" (con overlap) e ne valuta la sicurezza tramite LLM. Eventuali blocchi malevoli vengono messi in quarantena. Se l'elaborazione fallisce e viene ritentata, i vettori orfani vengono rimossi da Qdrant; eliminando un documento fallito viene rimosso anche il relativo file.
- **Chat**: L'utente finale (loggandoti come `user` o `admin`) può interrogare i documenti caricati. Prima di generare la risposta, la richiesta dell'utente ("prompt") viene filtrata (Prompt Injection check fail-closed, classificazione dell'intento). La risposta generata viene anch'essa supervisionata ("LLM Judge", che valuta la risposta insieme alla domanda originale) prima di essere mostrata. Le risposte del modello sono renderizzate in Markdown.

