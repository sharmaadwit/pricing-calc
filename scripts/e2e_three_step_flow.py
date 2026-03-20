#!/usr/bin/env python3
"""
Run volumes → prices → results with Flask test client; print step-wise session/template data flow.
Uses the same scenario helpers as voice_e2e_report.py.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SCRIPTS))

os.environ.setdefault(
    "DATABASE_URL",
    f"sqlite:///{ROOT / 'e2e_analytics.sqlite'}",
)

from voice_e2e_report import (  # noqa: E402
    _base_volume_fields,
    _csrf_from_page,
    _extract_input_value,
)


def _summarize_session(sess: dict) -> dict:
    """Lightweight, JSON-safe view of session after a step."""
    out: dict = {}
    for key in sorted(sess.keys()):
        if key == "inputs" and isinstance(sess[key], dict):
            inp = sess[key]
            out["inputs"] = {
                "country": inp.get("country"),
                "channel_type": inp.get("channel_type"),
                "voice_partner": inp.get("voice_partner"),
                "ai_volume": inp.get("ai_volume"),
                "whatsapp_voice_outbound_minutes": inp.get("whatsapp_voice_outbound_minutes"),
                "field_count": len(inp),
            }
        elif key == "profile" and isinstance(sess[key], dict):
            out["profile"] = {k: sess[key].get(k) for k in ("name", "email", "country", "region")}
        elif key == "pricing_inputs" and isinstance(sess[key], dict):
            out["pricing_inputs"] = dict(sess[key])
        elif key == "manday_rates" and isinstance(sess[key], dict):
            out["manday_rates"] = dict(sess[key])
        elif key == "results" and isinstance(sess[key], dict):
            r = sess[key]
            out["results"] = {
                "has_line_items": "line_items" in r,
                "line_items_count": len(r.get("line_items") or []),
                "revenue": r.get("revenue"),
                "has_voice_pricing": "voice_pricing" in r,
            }
        elif key == "voice_pricing" and isinstance(sess[key], dict):
            out["voice_pricing"] = {k: sess[key].get(k) for k in list(sess[key].keys())[:12]}
        elif key in (
            "calculation_id",
            "chosen_platform_fee",
            "rate_card_platform_fee",
            "bundle_choice",
            "csrf_token",
        ):
            out[key] = sess[key]
        elif key in ("authenticated",):
            out[key] = bool(sess[key])
    return out


def _page_markers(html: str) -> dict:
    # Order matters: prices page can mention inclusions in copy.
    step = None
    if "prices-form" in html or 'id="prices-form"' in html:
        step = "prices"
    elif "step='results'" in html or 'step="results"' in html:
        step = "results"
    elif "Rate Card Pricing" in html and "platform_fee" in html:
        step = "prices"
    elif 'name="step" value="volumes"' in html:
        step = "volumes"
    return {
        "rendered_step_hint": step,
        "has_prices_form": "prices-form" in html or 'id="prices-form"' in html,
        "has_voice_rate_card": "vr_wa_out_per_min" in html,
    }


def run_three_step(client, csrf: str, vol_data: dict) -> tuple[list[dict], list[str]]:
    log: list[str] = []
    snapshots: list[dict] = []

    vol_data = {**vol_data, "csrf_token": csrf}
    r1 = client.post("/", data=vol_data, follow_redirects=True)
    page1 = r1.get_data(as_text=True)
    with client.session_transaction() as sess:
        snapshots.append(
            {
                "after": "1_volumes_POST",
                "http_status": r1.status_code,
                "session": _summarize_session(dict(sess)),
                "response": _page_markers(page1),
            }
        )
    log.append(f"volumes POST → {r1.status_code}")
    if r1.status_code != 200:
        return snapshots, log

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

    log.append(
        "prices form excerpt: platform_fee=%s ai_price=%s bot_ui=%s"
        % (
            price_form.get("platform_fee"),
            price_form.get("ai_price"),
            price_form.get("bot_ui_manday_rate"),
        )
    )

    r2 = client.post("/", data=price_form, follow_redirects=True)
    page2 = r2.get_data(as_text=True)
    with client.session_transaction() as sess:
        snapshots.append(
            {
                "after": "2_prices_POST",
                "http_status": r2.status_code,
                "session": _summarize_session(dict(sess)),
                "response": _page_markers(page2),
            }
        )
    log.append(f"prices POST → {r2.status_code}")
    ok = r2.status_code == 200 and "internal error" not in page2.lower()
    snapshots.append(
        {
            "after": "3_flow_status",
            "ok": ok,
            "note": "results HTML expected after prices POST on main route",
        }
    )
    return snapshots, log


def main() -> int:
    from app import app, db

    with app.app_context():
        db.create_all()

    csrf = "e2e-3step-csrf"
    scenario = _base_volume_fields(
        channel_type="text_voice",
        voice_partner="leverage",
        voice_leverage_complexity="simple",
        voice_leverage_extra_language="No",
        ai_volume="1000",
        advanced_volume="500",
        basic_marketing_volume="2000",
        basic_utility_volume="300",
        num_voice_journeys="0",
        num_voice_apis="0",
    )

    client = app.test_client()
    with client.session_transaction() as sess:
        sess["authenticated"] = True
        sess["csrf_token"] = csrf

    with client.session_transaction() as sess:
        before = _summarize_session(dict(sess))
    snapshots, log = run_three_step(client, csrf, scenario)

    report = {
        "scenario": "text_voice + leverage + non-zero message volumes",
        "session_before_volumes": before,
        "steps": snapshots,
        "log": log,
    }

    out_path = ROOT / "e2e_output" / "three_step_dataflow.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))
    print(f"\nWrote {out_path}", file=sys.stderr)
    return 0 if snapshots[-1].get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
