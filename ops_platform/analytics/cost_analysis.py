from __future__ import annotations


class CostAnalyzer:
    def estimate(self, tokens_consumed: int, price_per_million: float = 8.0) -> dict[str, float]:
        estimated_cost = round((tokens_consumed / 1_000_000) * price_per_million, 2)
        return {"price_per_million": price_per_million, "estimated_cost": estimated_cost}
