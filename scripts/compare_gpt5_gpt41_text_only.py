#!/usr/bin/env python3
"""
Text-only India: compare ACE Agent Premium (gpt-5) vs Premium Experimental (gpt-4.1)
across complexities. Writes text_only_gpt5_vs_gpt41.html in project root.

Run: python3 scripts/compare_gpt5_gpt41_text_only.py
"""
from __future__ import annotations

import html as html_module
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import calculate_platform_fee  # noqa: E402
from calculator import calculate_pricing, get_suggested_price  # noqa: E402
from pricing_config import compute_ai_price_components, get_ai_model_cost  # noqa: E402

MODEL_GPT5 = "ACE Agent Premium (gpt-5)"
MODEL_GPT41 = "ACE Agent Premium Experimental (gpt-4.1)"
COUNTRY = "India"
AI_VOLUME = 60_000.0
ADV_VOL = 1_000.0
MKT_VOL = 5_000.0
UT_VOL = 400.0
COMPLEXITIES = ("regular", "hard", "complex")


def row_for(model: str, cx: str) -> dict:
    tier_ai = get_suggested_price(COUNTRY, "ai", AI_VOLUME)
    raw = get_ai_model_cost("India", model, cx)
    comp = compute_ai_price_components(COUNTRY, model, cx, tier_ai)
    ai_price = float(comp["markup"])
    adv = get_suggested_price(COUNTRY, "advanced", ADV_VOL)
    bm = get_suggested_price(COUNTRY, "basic_marketing", MKT_VOL)
    bu = get_suggested_price(COUNTRY, "basic_utility", UT_VOL)
    pf, _ = calculate_platform_fee(COUNTRY, "NA", "NA", "NA", "Yes", "No", "NA")
    res = calculate_pricing(
        COUNTRY,
        AI_VOLUME,
        ADV_VOL,
        MKT_VOL,
        UT_VOL,
        float(pf),
        ai_price=ai_price,
        advanced_price=adv,
        basic_marketing_price=bm,
        basic_utility_price=bu,
    )
    return {
        "model": model,
        "complexity": cx,
        "raw_inr": raw,
        "tier_ai_slab": tier_ai,
        "used_model": comp["used_model"],
        "ai_markup_per_msg": ai_price,
        "revenue": res["revenue"],
        "suggested_revenue": res["suggested_revenue"],
        "margin": res["margin"],
        "platform_fee": res["platform_fee"],
    }


def main() -> None:
    rows = []
    for cx in COMPLEXITIES:
        rows.append(row_for(MODEL_GPT5, cx))
        rows.append(row_for(MODEL_GPT41, cx))

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        "<title>Text-only India — GPT-5 vs GPT-4.1 (ACE Premium)</title>",
        "<style>",
        "body{font-family:system-ui,sans-serif;max-width:1000px;margin:24px auto;padding:0 16px;color:#1a202c;}",
        "h1{font-size:1.35rem;}",
        "table{border-collapse:collapse;width:100%;font-size:0.95rem;}",
        "th,td{border:1px solid #cbd5e0;padding:8px 10px;text-align:left;}",
        "th{background:#edf2f7;}",
        "td.num{text-align:right;font-family:ui-monospace,monospace;}",
        ".meta{color:#4a5568;font-size:0.9rem;margin-bottom:20px;}",
        ".gpt5{background:#f0fff4;}",
        ".gpt41{background:#fffaf0;}",
        "</style></head><body>",
        "<h1>Text-only (India) — model comparison</h1>",
        f'<p class="meta">{html_module.escape(stamp)} · AI volume {AI_VOLUME:g} (slab AI tier '
        f"{get_suggested_price(COUNTRY, 'ai', AI_VOLUME):g} INR/msg) · "
        f"Advanced {ADV_VOL:g}, Marketing {MKT_VOL:g}, Utility {UT_VOL:g}. "
        "Same non-AI prices; only AI markup from selected model + complexity changes.</p>",
        "<table>",
        "<thead><tr>",
        "<th>Model</th><th>Complexity</th><th>Raw cost<br>(INR/msg)</th>",
        "<th>Model path</th><th>AI markup<br>(INR/msg)</th>",
        "<th class='num'>AI revenue</th><th class='num'>Total msg revenue</th>",
        "<th class='num'>Platform fee</th><th>Margin %</th>",
        "</tr></thead><tbody>",
    ]

    for r in rows:
        cls = "gpt5" if r["model"] == MODEL_GPT5 else "gpt41"
        ai_rev = r["ai_markup_per_msg"] * AI_VOLUME
        parts.append(
            f"<tr class='{cls}'>"
            f"<td>{html_module.escape(r['model'])}</td>"
            f"<td>{html_module.escape(r['complexity'])}</td>"
            f"<td class='num'>{r['raw_inr']:.7f}</td>"
            f"<td>{'yes' if r['used_model'] else 'no (slab)'}</td>"
            f"<td class='num'>{r['ai_markup_per_msg']:.6f}</td>"
            f"<td class='num'>{ai_rev:,.2f}</td>"
            f"<td class='num'>{float(r['revenue']):,.2f}</td>"
            f"<td class='num'>{float(r['platform_fee']):,.2f}</td>"
            f"<td class='num'>{html_module.escape(str(r['margin']))}</td>"
            "</tr>"
        )

    parts.extend(
        [
            "</tbody></table>",
            "<p><b>Note:</b> Raw cost is from <code>AI_AGENT_PRICING['India']</code>. "
            "Markup follows flat ₹1 when raw ≤ 1, else 2× raw, when it beats the volume slab.</p>",
            "</body></html>",
        ]
    )

    out = ROOT / "text_only_gpt5_vs_gpt41.html"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
