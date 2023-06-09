from emoji import demojize


def contains_fonts(allowed_symbols: str, content: str) -> tuple[bool, list[str]]:
    content = content.strip().replace("\n", "").replace(" ", "").lower()
    allowed_symbols = set(allowed_symbols)
    allowed_symbols.add(" ")
    content = set(demojize(content))
    return not allowed_symbols >= content, list(content - allowed_symbols)
