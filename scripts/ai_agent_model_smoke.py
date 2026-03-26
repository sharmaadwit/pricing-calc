#!/usr/bin/env python3
"""
Smoke: AI_AGENT_PRICING × complexities with compute_ai_price_components + tier baseline.

Run from repo root:
  python3 scripts/ai_agent_model_smoke.py           # all scenarios
  python3 scripts/ai_agent_model_smoke.py --india   # India-only, per-model breakdown
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calculator import get_suggested_price  # noqa: E402
from pricing_config import (  # noqa: E402
    AI_AGENT_PRICING,
    AI_AGENT_SETTINGS,
    compute_ai_price_components,
    get_ai_model_cost,
    get_ai_pricing_key,
    meta_costs_table,
)

COMPLEXITIES = ("regular", "hard", "complex")


def _rule_and_candidate(pricing_key: str, raw: float) -> tuple[str, float]:
    s = AI_AGENT_SETTINGS[pricing_key]
    th, mult = float(s["threshold"]), float(s["multiplier"])
    if raw <= 0:
        return ("no raw → tier only", 0.0)
    if raw <= th:
        return (f"raw ≤ threshold {th} → flat markup = {th}", th)
    return (f"raw > {th} → markup = raw × {mult}", raw * mult)


def print_section(title: str) -> None:
    print()
    print("=" * 88)
    print(title)
    print("=" * 88)


def run_matrix(label: str, country: str, ai_volume: float) -> None:
    pricing_key = get_ai_pricing_key(country)
    tier_ai = get_suggested_price(country, "ai", ai_volume)
    meta = float(meta_costs_table.get(country, meta_costs_table["APAC"]).get("ai", 0.0) or 0.0)
    st = AI_AGENT_SETTINGS[pricing_key]
    print_section(
        f"{label}  |  country={country!r}  pricing_key={pricing_key!r}  "
        f"ai_volume={ai_volume:g}  tier_ai_markup={tier_ai:g}  meta_ai_cost={meta:g}"
    )
    print(
        f"Settings: threshold={st['threshold']}, multiplier={st['multiplier']}\n"
        "Apply model path iff raw_cost > 0 AND model_markup > tier_ai_markup;\n"
        "else final_markup = tier_ai_markup, used_model=False.\n"
    )
    hdr = f"{'model':<52} {'cx':<8} {'raw':>10} {'rule':<36} {'cand':>8} {'win':^5} {'markup':>8} {'final':>8}"
    print(hdr)
    print("-" * len(hdr))
    for model in AI_AGENT_PRICING[pricing_key]:
        for cx in COMPLEXITIES:
            raw = get_ai_model_cost(pricing_key, model, cx)
            rule, cand = _rule_and_candidate(pricing_key, raw)
            out = compute_ai_price_components(country, model, cx, tier_ai)
            win = cand > float(tier_ai or 0.0) and raw > 0
            short_rule = rule[:35] + ("…" if len(rule) > 36 else "")
            name = model[:49] + ("…" if len(model) > 52 else "")
            print(
                f"{name:<52} {cx:<8} {raw:>10.7f} {short_rule:<36} {cand:>8.6f} "
                f"{str(out['used_model']):^5} {out['markup']:>8.6f} {out['final_price']:>8.6f}"
            )


def india_per_model_detail(ai_volume: float) -> None:
    """Human-readable India (INR) steps: raw from table → candidate markup → vs tier → final."""
    country = "India"
    pricing_key = "India"
    tier_ai = get_suggested_price(country, "ai", ai_volume)
    meta = float(meta_costs_table.get(country, meta_costs_table["APAC"]).get("ai", 0.0) or 0.0)
    st = AI_AGENT_SETTINGS[pricing_key]
    th, mult = float(st["threshold"]), float(st["multiplier"])

    print_section("India — per-model calculations (INR)")
    print(
        f"Constants: threshold = {th} INR, multiplier = {mult}, meta_ai_cost = {meta} INR\n"
        f"Committed-amount route: ai_volume = {ai_volume:g} → tier_ai_markup = {tier_ai:g} INR\n"
        "\nSteps (each complexity):\n"
        "  raw = AI_AGENT_PRICING['India'][model][complexity]\n"
        f"  If 0 < raw ≤ {th}: candidate_markup = {th} (flat)\n"
        f"  If raw > {th}: candidate_markup = raw × {mult}\n"
        f"  If raw > 0 and candidate_markup > {tier_ai:g}: use candidate; else use tier {tier_ai:g}\n"
        f"  final_ai_per_message = {meta:g} + markup (INR)\n"
    )

    for model in AI_AGENT_PRICING[pricing_key]:
        print()
        print("-" * 88)
        print(model)
        print("-" * 88)
        for cx in COMPLEXITIES:
            raw = get_ai_model_cost(pricing_key, model, cx)
            out = compute_ai_price_components(country, model, cx, tier_ai)
            if raw <= 0:
                step = "raw = 0 → no model lookup; tier only"
                cand = 0.0
            elif raw <= th:
                step = f"0 < raw ({raw:.7f}) ≤ {th} → candidate = flat {th} INR"
                cand = th
            else:
                cand = raw * mult
                step = f"raw ({raw:.7f}) > {th} → candidate = raw × {mult} = {cand:.7f} INR"
            beats = raw > 0 and cand > float(tier_ai or 0.0)
            applied = "model markup applied" if out["used_model"] else "slab markup (tier) applied"
            print(f"  [{cx:7}] raw={raw:.7f} INR")
            print(f"           {step}")
            print(
                f"           candidate {cand:.7f} {'>' if beats else '≤'} tier {tier_ai:g} "
                f"→ {applied}, markup={out['markup']:.7f}, final={out['final_price']:.7f} INR"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="AI agent model pricing smoke tests")
    parser.add_argument(
        "--india",
        action="store_true",
        help="Print India-only per-model calculation breakdown",
    )
    parser.add_argument(
        "--ai-volume",
        type=float,
        default=60_000.0,
        help="AI monthly volume for tier_ai_markup (India detail mode). Default 60000 → tier 0.95",
    )
    args = parser.parse_args()

    if args.india:
        india_per_model_detail(args.ai_volume)
        return

    print_section("AI model smoke — calculation logic (pricing_config.compute_ai_price_components)")
    print(
        """
1) raw_cost = AI_AGENT_PRICING[pricing_key][model][complexity]
   pricing_key = 'India' if country == 'India' else 'International'

2) Read threshold and multiplier from AI_AGENT_SETTINGS[pricing_key]

3) Candidate model_markup:
     raw_cost <= 0     → 0 (no model pricing)
     0 < raw_cost ≤ threshold → model_markup = threshold  (flat “1” INR or USD floor)
     raw_cost > threshold     → model_markup = raw_cost × multiplier  (2×)

4) If raw_cost > 0 AND model_markup > tier_ai_markup (slab from get_suggested_price):
       used_model=True, markup=model_markup, final_price = meta_ai_cost + markup
   Else:
       used_model=False, markup=tier_ai_markup, final_price = meta_ai_cost + tier_ai_markup

tier_ai_markup uses committed_amount_slabs + ai_volume (same as Prices step when volume > 0).
For India, ai_volume 10_000 → tier AI is often 1.0, so flat model markup 1.0 does NOT beat tier (> is strict).
Using ai_volume 60_000 India → tier 0.95 so flat 1.0 wins for models with raw ≤ 1.
APAC USD tier is often 0.0105 = threshold → flat 0.0105 does not beat tier; 2× on large raw still wins.
"""
    )

    run_matrix("Scenario A — India, high enough committed slab", "India", 60_000.0)
    run_matrix("Scenario B — India, first slab (tier = 1.0)", "India", 10_000.0)
    run_matrix("Scenario C — APAC (USD table)", "APAC", 8_000.0)


if __name__ == "__main__":
    main()
