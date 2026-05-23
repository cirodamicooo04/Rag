import re
import unicodedata


def normalize_query(query: str) -> str:
    if query is None:
        return ""

    # 1. Normalizzazione unicode.
    # Esempio: caratteri full-width, accenti strani, simboli equivalenti.
    normalized = unicodedata.normalize("NFKC", query)

    # 2. Rimuove caratteri invisibili comuni.
    normalized = remove_invisible_chars(normalized)

    # 3. Normalizza spazi, tab e newline multipli.
    normalized = normalize_whitespace(normalized)

    # 4. Trim finale.
    normalized = normalized.strip()

    return normalized


def remove_invisible_chars(text: str) -> str:
    """
    Rimuove caratteri invisibili che possono essere usati per offuscare prompt injection.
    """

    invisible_chars = [
        "\u200b",  # zero-width space
        "\u200c",  # zero-width non-joiner
        "\u200d",  # zero-width joiner
        "\ufeff",  # byte order mark
        "\u2060",  # word joiner
    ]

    for char in invisible_chars:
        text = text.replace(char, "")

    return text


def normalize_whitespace(text: str) -> str:
    """
    Converte spazi multipli, tab e newline in un singolo spazio.
    """

    return re.sub(r"\s+", " ", text)