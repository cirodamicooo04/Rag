from transformers import pipeline, AutoTokenizer
import logging

from app.core.config import LLM_GUARD_MODEL, HF_TOKEN

MAX_TOKENS = 512
OVERLAP_TOKENS = 128
SAFE_LABEL = "LABEL_0"
SAFE_THRESHOLD = 0.8

logger = logging.getLogger(__name__)

try:
    tokenizer = AutoTokenizer.from_pretrained(LLM_GUARD_MODEL, token=HF_TOKEN)
    classifier = pipeline("text-classification", model=LLM_GUARD_MODEL, tokenizer=tokenizer, token=HF_TOKEN)
except Exception as e:
    logger.warning(f"Failed to load Llama Guard model (invalid or missing HF_TOKEN?). The guardrail will fail closed and every query will be blocked. Error: {e}")
    tokenizer = None
    classifier = None


def split_into_chunks(text: str) -> list[str]:
    token_ids = tokenizer.encode(text, add_special_tokens=False)

    if len(token_ids) <= MAX_TOKENS:
        return [text]

    chunks = []
    step = MAX_TOKENS - OVERLAP_TOKENS

    for start in range(0, len(token_ids), step):
        end = start + MAX_TOKENS
        chunk_ids = token_ids[start:end]

        chunks.append(tokenizer.decode(chunk_ids, skip_special_tokens=True))

        if end >= len(token_ids):
            break

    return chunks

def is_safe(query: str) -> bool:
    #Fail-closed: senza modello non possiamo validare la query, quindi la consideriamo non sicura
    if classifier is None or tokenizer is None:
        logger.warning("Llama Guard non disponibile: la query viene considerata non sicura (fail-closed).")
        return False

    chunks = split_into_chunks(query)

    for chunk in chunks:
        result = classifier(chunk,truncation=True,max_length=MAX_TOKENS)[0]

        if not (result["label"] == SAFE_LABEL and float(result["score"]) >= SAFE_THRESHOLD):
            return False

    return True