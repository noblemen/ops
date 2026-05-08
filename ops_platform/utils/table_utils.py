from __future__ import annotations


def build_key_value_table(payload: dict[str, object]) -> list[str]:
    return [f"{key}: {value}" for key, value in payload.items()]
