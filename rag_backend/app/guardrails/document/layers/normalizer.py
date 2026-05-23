import re
import unicodedata


INVISIBLE_CHARS = [
    "\u200b",  # zero-width space
    "\u200c",  # zero-width non-joiner
    "\u200d",  # zero-width joiner
    "\ufeff",  # byte order mark
    "\u2060",  # word joiner
]


def normalize_document_text(text: str) -> str:
    if text is None:
        return ""

    normalized = unicodedata.normalize("NFKC", text)
    normalized = remove_invisible_chars(normalized)
    normalized = normalize_document_whitespace(normalized)

    return normalized.strip()


def remove_invisible_chars(text: str) -> str:
    for char in INVISIBLE_CHARS:
        text = text.replace(char, "")

    return text


def normalize_document_whitespace(text: str) -> str:
    """
    Normalizza gli spazi preservando la struttura del documento.
    Utile prima di chunking ed embedding.
    """

    # Uniforma newline Windows/Mac/Linux
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Sostituisce tab e spazi multipli con singolo spazio
    text = re.sub(r"[ \t]+", " ", text)

    # Pulisce gli spazi a inizio/fine riga
    text = "\n".join(line.strip() for line in text.split("\n"))

    # Riduce newline eccessivi
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text