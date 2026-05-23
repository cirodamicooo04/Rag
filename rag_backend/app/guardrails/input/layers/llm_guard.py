from transformers import pipeline, AutoTokenizer

from app.core.config import LLM_GUARD_MODEL, HF_TOKEN

MAX_TOKENS = 512
OVERLAP_TOKENS = 128
SAFE_LABEL = "LABEL_0"
SAFE_THRESHOLD = 0.8

tokenizer = AutoTokenizer.from_pretrained(LLM_GUARD_MODEL)

classifier = pipeline("text-classification",model=LLM_GUARD_MODEL,tokenizer=tokenizer, token=HF_TOKEN)


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
    chunks = split_into_chunks(query)

    for chunk in chunks:
        result = classifier(chunk,truncation=True,max_length=MAX_TOKENS)[0]

        if not (result["label"] == SAFE_LABEL and float(result["score"]) >= SAFE_THRESHOLD):
            return False

    return True