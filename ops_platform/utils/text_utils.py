from __future__ import annotations


def compact_sentence(parts: list[str]) -> str:
    return " ".join(item.strip() for item in parts if item and item.strip())
