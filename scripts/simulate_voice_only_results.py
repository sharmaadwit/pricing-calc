"""
Simulate a Voice Only pricing flow and output the rendered Results page HTML.

Usage (from repo root, venv active):
    python scripts/simulate_voice_only_results.py > results_voice_only.html

The script uses Flask's test client to perform the actual route steps so the
rendered HTML matches the live application behavior.
"""

from bs4 import BeautifulSoup  # type: ignore
from typing import Dict

from app import app  # Import the Flask app


def extract_value(soup: BeautifulSoup, name: str) -> str:
    el = soup.find('input', { 'name': name })
    return (el.get('value') or '').strip() if el else ''


def extract_required_prices(soup: BeautifulSoup) -> Dict[str, str]:
    # Pull platform fee and rate card fields from the Prices page
    data = {
        'platform_fee': extract_value(soup, 'platform_fee'),
        'ai_price': extract_value(soup, 'ai_price'),
        'advanced_price': extract_value(soup, 'advanced_price'),
        'basic_marketing_price': extract_value(soup, 'basic_marketing_price'),
        'basic_utility_price': extract_value(soup, 'basic_utility_price'),
        'bot_ui_manday_rate': extract_value(soup, 'bot_ui_manday_rate'),
        'custom_ai_manday_rate': extract_value(soup, 'custom_ai_manday_rate'),
    }
    return { k: v.replace(',', '') for k, v in data.items() }


def main() -> None:
    app.testing = True
    with app.test_client() as client:
        # Authenticate the session
        with client.session_transaction() as sess:
            sess['authenticated'] = True

        # Step 1: POST Volumes with Voice Only (India)
        volumes_form = {
            'step': 'volumes',
            'user_name': 'Simulation Runner',
            'country': 'India',

            # Channel selection
            'channel_type': 'voice_only',

            # Ensure AI module setting is explicit for voice flows
            'ai_module': 'Yes',

            # Voice configuration
            'voice_ai_enabled': 'Yes',
            'num_voice_journeys': '2',
            'num_voice_apis': '1',
            'num_additional_voice_languages': '1',
            'agent_handover_pstn': 'Knowlarity',   # or 'Other'
            'whatsapp_voice_platform': 'Other',     # 3rd party -> setup fee applies
            'virtual_number_required': 'Yes',

            # PSTN minutes (bundled/overage will be computed)
            'pstn_inbound_ai_minutes': '12000',
            'pstn_inbound_committed': '10000',
            'pstn_outbound_ai_minutes': '25000',
            'pstn_outbound_committed': '20000',
            'pstn_manual_minutes': '0',
            'pstn_manual_committed': '0',

            # WhatsApp Voice minutes
            'whatsapp_voice_outbound_minutes': '40000',
            'whatsapp_voice_inbound_minutes': '10000',

            # Text volumes can be zero for voice-only flow
            'ai_volume': '0',
            'advanced_volume': '0',
            'basic_marketing_volume': '0',
            'basic_utility_volume': '0',
        }
        r = client.post('/', data=volumes_form, follow_redirects=True)
        assert r.status_code == 200, f"Volumes step failed: {r.status_code}"

        # Parse Prices page to get suggested values (required for validation)
        soup = BeautifulSoup(r.data, 'html.parser')
        prices = extract_required_prices(soup)

        # Step 2: POST Prices -> should render Results
        prices_form = {
            'step': 'prices',
            **prices,
        }
        r2 = client.post('/', data=prices_form, follow_redirects=True)
        assert r2.status_code == 200, f"Prices step failed: {r2.status_code}"

        # Output the Results page HTML to stdout
        # The caller can redirect to a file: > results_voice_only.html
        print(r2.data.decode('utf-8'))


if __name__ == '__main__':
    main()


