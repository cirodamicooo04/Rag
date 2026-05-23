HEADER_MAPPING = {
    "TITOLO": "title",
    "SCOPE": "scope",
    "FONTE": "source_url",
    "CATEGORIA": "category",
    "DATA SCRAPING": "scraping_date",
}

def parse_document_metadata(text: str) -> dict:
    metadata = {}

    for line in text.splitlines():
        line = line.strip()

        if line == "CONTENUTO:":
            break

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        mapped_key = HEADER_MAPPING.get(key)

        if mapped_key:
            metadata[mapped_key] = value

    return metadata

def remove_document_header(text: str) -> str:
    marker = "CONTENUTO:"

    if marker not in text:
        return text.strip()

    return text.split(marker, 1)[1].strip()

