#!/usr/bin/env python3
"""
Run volumes → prices → results via the Flask test client and save the real
rendered index.html (step=results) to e2e_results_page.html in the project root.

Uses the same flow as scripts/full_e2e_compare.py (Text + Voice, WA + PSTN).

Run from repo root:
  python3 scripts/e2e_results_page_html.py
"""
from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault(
    "DATABASE_URL",
    f"sqlite:///{ROOT / 'e2e_analytics.sqlite'}",
)

from voice_e2e_report import (  # noqa: E402
    _base_volume_fields,
    _csrf_from_page,
    _extract_input_value,
)


def _scenario_text_voice_wa_pstn() -> dict:
    return {
        **_base_volume_fields(
            channel_type="text_voice",
            voice_partner="gupshup_native",
            ai_volume="3000",
            advanced_volume="1000",
            basic_marketing_volume="5000",
            basic_utility_volume="400",
            num_voice_journeys="3",
            num_voice_apis="2",
        ),
        "whatsapp_voice_outbound_minutes": "3000",
        "whatsapp_voice_inbound_minutes": "800",
        "pstn_inbound_ai_minutes": "2000",
        "pstn_inbound_committed": "1500",
        "pstn_outbound_ai_minutes": "3000",
        "pstn_outbound_committed": "2000",
        "pstn_manual_minutes": "500",
        "pstn_manual_committed": "500",
        "agent_handover_pstn": "Knowlarity",
    }


def run_and_capture_html(csrf: str = "e2e-results-html-csrf") -> tuple[int, str]:
    from app import app, db

    with app.app_context():
        db.create_all()

    client = app.test_client()
    with client.session_transaction() as s:
        s["authenticated"] = True
        s["csrf_token"] = csrf

    vol = {**_scenario_text_voice_wa_pstn(), "csrf_token": csrf, "step": "volumes"}
    r1 = client.post("/", data=vol, follow_redirects=True)
    if r1.status_code != 200:
        return r1.status_code, r1.get_data(as_text=True)

    page1 = r1.get_data(as_text=True)
    csrf2 = _csrf_from_page(page1) or csrf
    price_form = {"csrf_token": csrf2, "step": "prices"}
    for n in [
        "platform_fee",
        "ai_price",
        "advanced_price",
        "basic_marketing_price",
        "basic_utility_price",
        "bot_ui_manday_rate",
        "custom_ai_manday_rate",
    ]:
        price_form[n] = _extract_input_value(page1, n)
    for vr in [
        "vr_pstn_in_bundled",
        "vr_pstn_in_overage",
        "vr_pstn_out_bundled",
        "vr_pstn_out_overage",
        "vr_pstn_manual_bundled",
        "vr_pstn_manual_overage",
        "vr_wa_out_per_min",
        "vr_wa_in_per_min",
    ]:
        if f'name="{vr}"' in page1:
            price_form[vr] = _extract_input_value(page1, vr)

    r2 = client.post("/", data=price_form, follow_redirects=True)
    return r2.status_code, r2.get_data(as_text=True)


def _inject_banner(html: str, note: str) -> str:
    """Insert a small notice after <body> so the file is clearly a snapshot."""
    if re.search(r"<body[^>]*>", html, re.IGNORECASE):
        return re.sub(
            r"(<body[^>]*>)",
            r'\1<div style="background:#1a365d;color:#fff;padding:10px 16px;font:14px system-ui;margin:0;">'
            + note
            + "</div>",
            html,
            count=1,
            flags=re.IGNORECASE,
        )
    return html


def main() -> int:
    status, html = run_and_capture_html()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    banner = (
        f"E2E results snapshot · generated {stamp} · HTTP {status} · "
        f"scenario: Text+Voice (India, native, WA+PSTN). "
        f"Static assets (/static) need <code>python3 -m http.server</code> from repo root if styles look bare."
    )
    out = ROOT / "e2e_results_page.html"
    out.write_text(_inject_banner(html, banner), encoding="utf-8")
    print(f"Wrote {out} (status={status}, {len(html):,} chars)", file=sys.stderr)
    if status != 200:
        return 1
    if "step='results'" not in html and 'step="results"' not in html and "Pricing Table" not in html:
        print("Warning: response may not be the results step.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
