#!/usr/bin/env python3
"""
End-to-end pricing runs (Flask test client): Voice-only + Text+Voice.
Writes voice_e2e_results.html and e2e_output/*.html in the project root.
Open voice_e2e_results.html locally in a browser.
"""
from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "e2e_output"
OUT_INDEX = ROOT / "voice_e2e_results.html"

os.environ.setdefault(
    "DATABASE_URL",
    f"sqlite:///{ROOT / 'e2e_analytics.sqlite'}",
)


def _extract_input_value(page: str, name: str) -> str:
    m = re.search(rf'<input[^>]*\bname="{re.escape(name)}"[^>]*>', page, re.IGNORECASE)
    if not m:
        return ""
    tag = m.group(0)
    vm = re.search(r'\bvalue="([^"]*)"', tag, re.IGNORECASE)
    if vm:
        return html.unescape(vm.group(1))
    vm = re.search(r"\bvalue='([^']*)'", tag, re.IGNORECASE)
    return html.unescape(vm.group(1)) if vm else ""


def _csrf_from_page(page: str) -> str:
    return _extract_input_value(page, "csrf_token")


def _base_volume_fields(
    *,
    channel_type: str,
    voice_partner: str = "gupshup_native",
    voice_leverage_complexity: str = "",
    voice_leverage_extra_language: str = "No",
    ai_volume: str = "0",
    advanced_volume: str = "0",
    basic_marketing_volume: str = "0",
    basic_utility_volume: str = "0",
    num_voice_journeys: str = "2",
    num_voice_apis: str = "2",
) -> dict:
    add_lang = "1" if voice_partner == "gupshup_native" else "0"
    return {
        "step": "volumes",
        "user_name": "E2E Voice Report",
        "user_email": "voice-e2e@example.com",
        "country": "India",
        "region": "North",
        "channel_type": channel_type,
        "voice_partner": voice_partner,
        "voice_leverage_complexity": voice_leverage_complexity,
        "voice_leverage_extra_language": voice_leverage_extra_language,
        "voice_ai_enabled": "Yes",
        "onboarding_price": "No",
        "ux_price": "No",
        "testing_qa_price": "No",
        "aa_setup_price": "No",
        "num_apis_price": "2",
        "num_journeys_price": "2",
        "num_ai_workspace_commerce_price": "0",
        "num_ai_workspace_faq_price": "0",
        "voice_notes_price": "No",
        "ai_volume": ai_volume,
        "advanced_volume": advanced_volume,
        "basic_marketing_volume": basic_marketing_volume,
        "basic_utility_volume": basic_utility_volume,
        "bfsi_tier": "NA",
        "personalize_load": "NA",
        "human_agents": "NA",
        "ai_module": "Yes",
        "smart_cpaas": "No",
        "increased_tps": "NA",
        "agent_handover_pstn": "None",
        "whatsapp_voice_platform": "None",
        "virtual_number_required": "No",
        "pstn_inbound_ai_minutes": "0",
        "pstn_inbound_committed": "0",
        "pstn_outbound_ai_minutes": "0",
        "pstn_outbound_committed": "0",
        "pstn_manual_minutes": "0",
        "pstn_manual_committed": "0",
        "whatsapp_voice_outbound_minutes": "5000",
        "whatsapp_voice_inbound_minutes": "1000",
        "num_voice_journeys": num_voice_journeys,
        "num_voice_apis": num_voice_apis,
        "num_additional_voice_languages": add_lang,
        "ai_agent_model": "ACE Agentic pro (gpt-5-mini)",
        "ai_agent_complexity": "regular",
    }


def run_flow(client, csrf: str, vol_data: dict) -> tuple[int, str, str]:
    vol_data = {**vol_data, "csrf_token": csrf}
    r1 = client.post("/", data=vol_data, follow_redirects=True)
    if r1.status_code != 200:
        return r1.status_code, "volumes step failed", r1.get_data(as_text=True)

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

    if vol_data.get("voice_notes_price") == "Yes":
        price_form["voice_notes_rate"] = _extract_input_value(page1, "voice_notes_rate")

    r2 = client.post("/", data=price_form, follow_redirects=True)
    body = r2.get_data(as_text=True)
    if r2.status_code != 200:
        return r2.status_code, "prices step failed", body
    if "internal error" in body.lower() or "calculation failed" in body.lower():
        return r2.status_code, "results may show error flash", body
    if "step='results'" in body or 'step="results"' in body or "Inclusions Card" in body:
        return r2.status_code, "ok", body
    return r2.status_code, "unexpected body (no results markers)", body[:15000]


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from app import app, db

    OUT_DIR.mkdir(exist_ok=True)
    with app.app_context():
        db.create_all()

    csrf = "e2e-voice-csrf-token"
    scenarios = [
        (
            "voice_e2e_A_voice_only_leverage.html",
            "A) Voice only — Leverage (medium + extra language)",
            _base_volume_fields(
                channel_type="voice_only",
                voice_partner="leverage",
                voice_leverage_complexity="medium",
                voice_leverage_extra_language="Yes",
                num_voice_journeys="0",
                num_voice_apis="0",
            ),
        ),
        (
            "voice_e2e_B_voice_only_native.html",
            "B) Voice only — Gupshup native",
            _base_volume_fields(
                channel_type="voice_only",
                voice_partner="gupshup_native",
                voice_leverage_complexity="",
                num_voice_journeys="2",
                num_voice_apis="2",
            ),
        ),
        (
            "voice_e2e_C_text_voice_leverage.html",
            "C) Text + Voice — Leverage (simple) with volumes",
            _base_volume_fields(
                channel_type="text_voice",
                voice_partner="leverage",
                voice_leverage_complexity="simple",
                voice_leverage_extra_language="No",
                ai_volume="25000",
                advanced_volume="10000",
                basic_marketing_volume="50000",
                basic_utility_volume="20000",
                num_voice_journeys="0",
                num_voice_apis="0",
            ),
        ),
    ]

    index_parts = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        "<title>Voice E2E — Pricing Calculator</title>",
        "<style>",
        "body{font-family:system-ui,sans-serif;margin:24px;max-width:1200px;color:#222;}",
        "h1{border-bottom:2px solid #5a2a8a;padding-bottom:8px;}",
        "section{margin:28px 0;padding:16px;background:#fafafa;border:1px solid #ddd;border-radius:8px;}",
        ".meta{font-size:0.9rem;color:#555;}",
        "iframe{width:100%;min-height:880px;border:1px solid #ccc;background:#fff;}",
        "pre.fail{background:#ffeaea;padding:12px;overflow:auto;max-height:420px;font-size:12px;}",
        "</style></head><body>",
        "<h1>Voice pricing — end-to-end runs</h1>",
        '<p class="meta">Open this file via <code>file://</code>. Generated by <code>scripts/voice_e2e_report.py</code>.</p>',
    ]

    for fname, title, vol in scenarios:
        client = app.test_client()
        with client.session_transaction() as sess:
            sess["authenticated"] = True
            sess["csrf_token"] = csrf

        status, note, content = run_flow(client, csrf, vol)
        out_path = OUT_DIR / fname
        if note == "ok":
            out_path.write_text(content, encoding="utf-8")
        else:
            out_path.write_text(f"<!-- {note} -->\n<pre>{html.escape(content)}</pre>", encoding="utf-8")

        index_parts.append("<section>")
        index_parts.append(f"<h2>{html.escape(title)}</h2>")
        index_parts.append(f'<p class="meta">HTTP {status} — {html.escape(note)} · file <code>e2e_output/{fname}</code></p>')
        if note == "ok":
            index_parts.append(f'<iframe src="e2e_output/{html.escape(fname)}"></iframe>')
        else:
            index_parts.append(f'<pre class="fail">{html.escape(content[:8000])}</pre>')
        index_parts.append("</section>")

    index_parts.append("</body></html>")
    OUT_INDEX.write_text("\n".join(index_parts), encoding="utf-8")
    print(f"Wrote {OUT_INDEX}")
    print(f"Artifacts in {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
