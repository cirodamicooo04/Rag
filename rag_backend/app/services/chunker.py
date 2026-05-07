import re
from typing import List

from app.core.config import MAX_TOKENS, OVERLAP_TOKENS
from app.core.ml_models import tokenizer


def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))


def split_sentences(text: str) -> List[str]:
    # 1. Dividiamo prima per i separatori di sezione (---) o doppi a capo (\n\n)
    # Questi spesso delimitano il cambio di docente o di argomento
    segments = re.split(r'---|\n\n', text)

    all_sentences = []
    for segment in segments:
        # 2. Dividiamo ogni segmento usando punteggiatura standard O nuovi riga (\n)
        # Il \n è fondamentale per gestire gli orari e le liste docenti
        parts = re.split(r'(?<=[.!?])\s+|\n', segment)
        for p in parts:
            p_strip = p.strip()
            if p_strip:
                all_sentences.append(p_strip)

    return all_sentences

def semantic_chunk(text: str) -> List[str]:
    #Splittiamo in ogni \n
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    chunks = []
    current_chunk = []
    current_tokens = 0

    for paragraph in paragraphs:
        #Isoliamo ogni singola frase per paragrafo
        sentences = split_sentences(paragraph)

        for sentence in sentences:
            #Contiamo i token per ogni frase
            sentence_tokens = count_tokens(sentence)

            #Se abbiamo superato i token massimi dobbiamo chiudere il chunk attuale
            if current_tokens + sentence_tokens > MAX_TOKENS:
                if current_chunk:
                    #Chiudiamo il current chunk
                    chunks.append(" ".join(current_chunk))

                    # overlap
                    overlap_text = " ".join(current_chunk)
                    overlap_tokens = tokenizer.encode(
                        overlap_text,
                        add_special_tokens=False
                    )[-OVERLAP_TOKENS:] #Prendiamo solo gli utlimi token di overlap (80)

                    overlap_string = tokenizer.decode(overlap_tokens) #Li trasformiamo di nuovo in testo
                    current_chunk = [overlap_string] #Li mettiamo come punto di partenza per il prossimo chunk
                    current_tokens = count_tokens(overlap_string) #Aggiorniamo i token correnti
                else:
                    # frase singola enorme, la mettiamo in un solo chunk
                    chunks.append(sentence)
                    current_chunk = []
                    current_tokens = 0
                    continue

            # Altrimenti aggiungiamo normalmente al chunk corrente
            current_chunk.append(sentence)
            current_tokens += sentence_tokens

    #Aggiungiamo eventuali pezzi rimasti
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks