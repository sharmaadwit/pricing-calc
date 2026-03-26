#!/usr/bin/env python3
"""
Full E2E comparison: runs 6 scenarios page-by-page (volumes → prices → results)
through the Flask test client. Captures session state after each step.

Scenarios:
  1) Text Only
  2) Text + Voice (native, WA only)
  3) Text + Voice (native, WA + PSTN)
  4) Voice Only — Native (WA + PSTN)
  5) Voice Only — Leverage simple
  6) Voice Only — Leverage complex + extra language

Run:  python3 scripts/full_e2e_compare.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

os.environ.setdefault("DATABASE_URL", f"sqlite:///{ROOT / 'e2e_analytics.sqlite'}")

from voice_e2e_report import _base_volume_fields, _csrf_from_page, _extract_input_value


def _run_full(client, csrf, vol_data):
    """Run volumes → prices → results, return detailed per-step report."""
    report = {}

    # ── Step 1: Volumes ──
    vol_data = {**vol_data, "csrf_token": csrf}
    r1 = client.post("/", data=vol_data, follow_redirects=True)
    report["step1_volumes"] = {"status": r1.status_code}
    if r1.status_code != 200:
        report["error"] = "volumes POST failed"
        return report

    with client.session_transaction() as sess:
        inputs = dict(sess.get("inputs") or {})

    vol_keys = [
        "channel_type", "country", "voice_partner",
        "ai_volume", "advanced_volume", "basic_marketing_volume", "basic_utility_volume",
        "pstn_inbound_ai_minutes", "pstn_inbound_committed",
        "pstn_outbound_ai_minutes", "pstn_outbound_committed",
        "pstn_manual_minutes", "pstn_manual_committed",
        "whatsapp_voice_outbound_minutes", "whatsapp_voice_inbound_minutes",
        "num_apis_price", "num_journeys_price",
        "num_voice_journeys", "num_voice_apis",
        "num_additional_voice_languages",
        "agent_handover_pstn", "whatsapp_voice_platform", "virtual_number_required",
        "voice_ai_enabled", "voice_leverage_complexity", "voice_leverage_extra_language",
        "num_ai_workspace_commerce_price", "num_ai_workspace_faq_price",
        "onboarding_price", "ux_price", "testing_qa_price", "aa_setup_price",
    ]
    report["step1_volumes"]["session_inputs"] = {k: inputs.get(k) for k in vol_keys}

    # ── Step 2: Prices ──
    page1 = r1.get_data(as_text=True)
    csrf2 = _csrf_from_page(page1) or csrf
    price_form = {"csrf_token": csrf2, "step": "prices"}
    for n in [
        "platform_fee", "ai_price", "advanced_price",
        "basic_marketing_price", "basic_utility_price",
        "bot_ui_manday_rate", "custom_ai_manday_rate",
    ]:
        price_form[n] = _extract_input_value(page1, n)
    for vr in [
        "vr_pstn_in_bundled", "vr_pstn_in_overage",
        "vr_pstn_out_bundled", "vr_pstn_out_overage",
        "vr_pstn_manual_bundled", "vr_pstn_manual_overage",
        "vr_wa_out_per_min", "vr_wa_in_per_min",
    ]:
        if f'name="{vr}"' in page1:
            price_form[vr] = _extract_input_value(page1, vr)

    r2 = client.post("/", data=price_form, follow_redirects=True)
    report["step2_prices"] = {
        "status": r2.status_code,
        "form_submitted": {k: v for k, v in sorted(price_form.items()) if k != "csrf_token"},
    }

    # ── Step 3: Results (from session) ──
    with client.session_transaction() as sess:
        pricing = dict(sess.get("pricing_inputs") or {})
        results = dict(sess.get("results") or {})
        voice = results.get("voice_pricing") or sess.get("voice_pricing")
        dcb = sess.get("dev_cost_breakdown") or {}
        mbd = sess.get("manday_breakdown") or {}

    report["step3_results"] = {
        "status": r2.status_code,
        "pricing_inputs": pricing,
        "revenue": results.get("revenue"),
        "suggested_revenue": results.get("suggested_revenue"),
        "margin": results.get("margin"),
        "suggested_margin": results.get("suggested_margin"),
        "platform_fee": results.get("platform_fee"),
        "channel_cost": results.get("channel_cost"),
        "ai_costs": results.get("ai_costs"),
        "total_costs": results.get("total_costs"),
    }
    if results.get("line_items"):
        report["step3_results"]["line_items"] = [
            {
                "label": li.get("label"),
                "volume": li.get("volume"),
                "chosen_price": li.get("chosen_price"),
                "suggested_price": li.get("suggested_price"),
                "meta_cost": li.get("meta_cost"),
                "final_price": li.get("final_price"),
                "revenue": li.get("revenue"),
            }
            for li in results["line_items"]
        ]

    report["dev_cost"] = {
        "build_cost": dcb.get("build_cost"),
        "ba_cost": dcb.get("ba_cost"),
        "qa_cost": dcb.get("qa_cost"),
        "pm_cost": dcb.get("pm_cost"),
        "uplift_amount": dcb.get("uplift_amount"),
        "total_cost": dcb.get("total_cost"),
        "currency": dcb.get("currency"),
        "mandays_breakdown": dcb.get("mandays_breakdown"),
    }
    report["manday_breakdown_session"] = dict(mbd)

    if voice:
        vc = voice.get("calling_costs") or {}
        report["voice_pricing"] = {
            "voice_partner_model": voice.get("voice_partner_model"),
            "voice_mandays": voice.get("voice_mandays"),
            "voice_dev_cost": voice.get("voice_dev_cost"),
            "voice_platform_fee": voice.get("voice_platform_fee"),
            "total_voice_cost": voice.get("total_voice_cost"),
            "calling_costs": {
                "pstn_inbound_ai": vc.get("pstn_inbound_ai"),
                "pstn_outbound_ai": vc.get("pstn_outbound_ai"),
                "pstn_manual_c2c": vc.get("pstn_manual_c2c"),
                "whatsapp_voice_outbound": vc.get("whatsapp_voice_outbound"),
                "whatsapp_voice_inbound": vc.get("whatsapp_voice_inbound"),
                "total": vc.get("total"),
            },
        }
        if voice.get("voice_leverage_partner_cost") is not None:
            report["voice_pricing"]["leverage_partner_cost"] = voice.get("voice_leverage_partner_cost")
            report["voice_pricing"]["leverage_build_margin"] = voice.get("voice_leverage_build_margin")
            report["voice_pricing"]["leverage_complexity"] = voice.get("voice_leverage_complexity")
    else:
        report["voice_pricing"] = None

    body = r2.get_data(as_text=True)
    report["ok"] = r2.status_code == 200 and bool(results.get("line_items")) and (
        "step='results'" in body or 'step="results"' in body or "Inclusions" in body
    )
    return report


SCENARIOS = [
    (
        "1) TEXT ONLY",
        {
            **_base_volume_fields(
                channel_type="text_only",
                voice_partner="gupshup_native",
                ai_volume="5000", advanced_volume="2000",
                basic_marketing_volume="10000", basic_utility_volume="500",
                num_voice_journeys="0", num_voice_apis="0",
            ),
            "whatsapp_voice_outbound_minutes": "0",
            "whatsapp_voice_inbound_minutes": "0",
            "pstn_inbound_ai_minutes": "0",
            "pstn_outbound_ai_minutes": "0",
            "pstn_manual_minutes": "0",
        },
    ),
    (
        "2) TEXT + VOICE native (WA only)",
        {
            **_base_volume_fields(
                channel_type="text_voice",
                voice_partner="gupshup_native",
                ai_volume="3000", advanced_volume="1000",
                basic_marketing_volume="5000", basic_utility_volume="400",
                num_voice_journeys="2", num_voice_apis="2",
            ),
            "pstn_inbound_ai_minutes": "0",
            "pstn_outbound_ai_minutes": "0",
            "pstn_manual_minutes": "0",
        },
    ),
    (
        "3) TEXT + VOICE native (WA + PSTN)",
        {
            **_base_volume_fields(
                channel_type="text_voice",
                voice_partner="gupshup_native",
                ai_volume="3000", advanced_volume="1000",
                basic_marketing_volume="5000", basic_utility_volume="400",
                num_voice_journeys="3", num_voice_apis="2",
            ),
            "pstn_inbound_ai_minutes": "2000",
            "pstn_inbound_committed": "1500",
            "pstn_outbound_ai_minutes": "3000",
            "pstn_outbound_committed": "2000",
            "pstn_manual_minutes": "500",
            "pstn_manual_committed": "500",
            "agent_handover_pstn": "Knowlarity",
        },
    ),
    (
        "4) VOICE ONLY — Native (WA + PSTN)",
        {
            **_base_volume_fields(
                channel_type="voice_only",
                voice_partner="gupshup_native",
                ai_volume="0", advanced_volume="0",
                basic_marketing_volume="0", basic_utility_volume="0",
                num_voice_journeys="2", num_voice_apis="3",
            ),
            "pstn_inbound_ai_minutes": "1000",
            "pstn_inbound_committed": "800",
            "pstn_outbound_ai_minutes": "2000",
            "pstn_outbound_committed": "1500",
            "pstn_manual_minutes": "300",
            "pstn_manual_committed": "300",
            "whatsapp_voice_platform": "Knowlarity",
        },
    ),
    (
        "5) VOICE ONLY — Leverage simple",
        _base_volume_fields(
            channel_type="voice_only",
            voice_partner="leverage",
            voice_leverage_complexity="simple",
            voice_leverage_extra_language="No",
            ai_volume="0", advanced_volume="0",
            basic_marketing_volume="0", basic_utility_volume="0",
            num_voice_journeys="0", num_voice_apis="0",
        ),
    ),
    (
        "6) VOICE ONLY — Leverage complex + extra lang",
        _base_volume_fields(
            channel_type="voice_only",
            voice_partner="leverage",
            voice_leverage_complexity="complex",
            voice_leverage_extra_language="Yes",
            ai_volume="0", advanced_volume="0",
            basic_marketing_volume="0", basic_utility_volume="0",
            num_voice_journeys="0", num_voice_apis="0",
        ),
    ),
]


def main():
    from app import app, db

    with app.app_context():
        db.create_all()

    csrf = "full-e2e-csrf"
    all_reports = {}

    for title, vol in SCENARIOS:
        client = app.test_client()
        with client.session_transaction() as s:
            s["authenticated"] = True
            s["csrf_token"] = csrf
        report = _run_full(client, csrf, vol)
        all_reports[title] = report

    print(json.dumps(all_reports, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
