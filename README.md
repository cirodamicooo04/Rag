1. Requisiti Preliminari
 - Docker installato.
 - Python 3.10 o superiore (consigliato 3.12).
 - LM Studio installato.

2. Configurazione LM Studio
Il backend comunica con un modello linguistico tramite le API locali di LM Studio.
Apri LM Studio.
 - Carica un modello (es. Llama 3 o Mistral ).
 - Vai nella scheda Local Server. 
 - Assicurati che la porta sia impostata su 1234 (o quella definita in config.py ).
 - Clicca su Start Server.

3. Avvio Infrastruttura (Docker)
È necessario avviare il database vettoriale Qdrant. Dalla cartella principale del progetto (dove si
trova il file docker-compose.yml ), esegui:

 - docker compose up -d
Questo comando avvierà Qdrant in background sulla porta 6333 .

4. Configurazione Backend
Spostati nella cartella del backend e installa le librerie necessarie:

- cd rag_backend
- pip install -r requirements.txt

5. Avvio del Server API
Per avviare il backend , usa uvicorn o avvia la configurazione da PyCharm :

- uvicorn app.main:app --reload

Il server sarà disponibile all'indirizzo: http://localhost:8000

6. Utilizzo e Test
Documentazione Interattiva
Puoi testare gli endpoint (caricamento documenti, query) direttamente dal browser:
- Swagger UI: http://localhost:8000/docs

La cartella docs/ e il database SQLite rag_database.db verranno
creati automaticamente al primo avvio se non presenti.