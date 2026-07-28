# RAG Backend - Sistema di Retrieval-Augmented Generation Sicuro

Questo progetto implementa un sistema RAG (Retrieval-Augmented Generation) avanzato, incentrato sulla sicurezza. Utilizza una pipeline di ingestion e un'interfaccia di chat dotate di diversi "guardrail" (barriere di sicurezza) per analizzare intenti, neutralizzare attacchi (Prompt Injection) e validare i documenti caricati.

Al momento, il sistema supporta esclusivamente l'upload di file di testo in formato `.txt`.

## Architettura e Tecnologie
- **Backend**: FastAPI (Python)
- **Modelli LLM**: Groq (per un'esecuzione ultra-rapida in cloud tramite API compatibili con OpenAI)
- **Modelli Locali**: Hugging Face (embedding con `intfloat/multilingual-e5-base` e controlli di sicurezza)
- **Database Vettoriale**: Qdrant
- **Autenticazione**: Keycloak (supportato da PostgreSQL)
- **Frontend**: SvelteKit (nella cartella `rag-frontend`)

---

## 1. Requisiti Preliminari

1. **Docker e Docker Compose** installati sul sistema.
2. **Node.js** (opzionale, ma necessario se si vuole avviare l'interfaccia frontend SvelteKit in locale).
3. **Chiave API di Groq**: 
   - Vai su [Groq Console](https://console.groq.com/keys) e crea una API Key gratuita.
4. **Token di Hugging Face (HF_TOKEN)**:
   - Il progetto utilizza il modello di sicurezza `meta-llama/Llama-Prompt-Guard-2-86M`. Poiché è un modello con restrizioni, **devi prima accettare i termini di utilizzo** sulla pagina ufficiale.
   - Vai su: [meta-llama/Llama-Prompt-Guard-2-86M su Hugging Face](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M) e clicca su "Agree" o "Acknowledge license".
   - Genera un token di accesso (Read) dalle tue [Impostazioni di Hugging Face](https://huggingface.co/settings/tokens).

---

## 2. Configurazione

1. Clona il repository e spostati nella cartella principale (dove si trova il file `docker-compose.yml`).
2. Crea un file chiamato `.env` copiando il modello `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Apri il file `.env` e inserisci le tue credenziali:
   - Compila `GROQ_API_KEY` con la chiave generata.
   - Compila `HF_TOKEN` con il token di Hugging Face (assicurandoti di aver prima accettato i termini del modello Llama-Prompt-Guard-2-86M, altrimenti il container andrà in errore durante il download).
   - *Nota: le credenziali di default per Keycloak e Postgres sono già impostate nel file di esempio.*

---

## 3. Avvio dell'Infrastruttura (Backend + Servizi)

Tutta l'infrastruttura di base (Backend FastAPI, Qdrant, Keycloak e PostgreSQL) è containerizzata con Docker.

Per avviare tutto, esegui dalla cartella principale:
```bash
docker compose up -d --build
```

- Il **Backend (FastAPI)** sarà disponibile su: `http://localhost:8000`
- La **Documentazione API (Swagger)** sarà su: `http://localhost:8000/docs`
- **Keycloak** (Pannello Admin) sarà su: `http://localhost:8089` (user: `admin`, pass: `admin`)
- **Qdrant** sarà in ascolto sulla porta `6333` e `6334`.

*Nota: Al primissimo avvio, il backend scaricherà i modelli di embedding e Llama Guard da Hugging Face. Potrebbe volerci qualche minuto in base alla tua connessione. La cartella `/rag_backend/data` contenente il database SQLite verrà creata automaticamente.*

---

## 4. Avvio del Frontend

Il frontend è sviluppato in SvelteKit e comunica con il backend e con Keycloak.

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
4. L'interfaccia utente sarà accessibile all'indirizzo mostrato nel terminale (solitamente `http://localhost:5173`).

---

## 5. Utilizzo

- **Gestione Documenti**: Dall'interfaccia (o tramite le API in Swagger), l'amministratore può caricare documenti. Il sistema accetta **solo file .txt**. Una volta caricato, il documento passa attraverso una pipeline che lo pulisce, lo divide in "chunk" e ne valuta la sicurezza tramite LLM. Eventuali blocchi malevoli vengono messi in quarantena.
- **Chat**: L'utente finale può interrogare i documenti caricati. Prima di generare la risposta, la richiesta dell'utente ("prompt") viene filtrata (Prompt Injection check, classificazione dell'intento). La risposta generata viene anch'essa supervisionata ("LLM Judge") prima di essere mostrata.