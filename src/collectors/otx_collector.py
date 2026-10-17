
import os
import ipaddress

import requests
from dotenv import load_dotenv


load_dotenv()

OTX_URL = "https://otx.alienvault.com/api/v1/pulses/activity"

SUPPORTED_TYPES = {
    "IPv4",
    "IPv6",
    "domain",
    "hostname",
    "FileHash-SHA256",
}


def fetch_otx_indicators():
    """Fetch a small read-only sample of OTX indicators."""

    api_key = os.getenv("OTX_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OTX_API_KEY is missing from your .env file."
        )

    headers = {
        "X-OTX-API-KEY": api_key,
        "Accept": "application/json",
    }

    response = requests.get(
        OTX_URL,
        headers=headers,
        params={"limit": 5, "page": 1},
        timeout=30,
    )

    response.raise_for_status()
    payload = response.json()

    if not isinstance(payload, dict):
        raise ValueError("Unexpected OTX API response format.")

    pulses = payload.get("results")

    if not isinstance(pulses, list):
        raise ValueError("OTX response has no results list.")

    indicators = []

    for pulse in pulses:
        if not isinstance(pulse, dict):
            continue

        for indicator in pulse.get("indicators", []):
            if not isinstance(indicator, dict):
                continue

            indicator_type = indicator.get("type")
            value = indicator.get("indicator")

            if indicator_type not in SUPPORTED_TYPES:
                continue

            if not isinstance(value, str) or not value.strip():
                continue

            value = value.strip()

            if indicator_type in {"IPv4", "IPv6"}:
                try:
                    ip = ipaddress.ip_address(value)

                    if not ip.is_global:
                        continue

                    if ip.version != int(indicator_type[-1]):
                        continue

                except ValueError:
                    continue

            indicators.append({
                "indicator_value": value,
                "indicator_type": indicator_type,
                "source": "AlienVault OTX",
                "pulse_name": pulse.get(
                    "name", "Unknown Pulse"
                ),
            })

            if len(indicators) >= 20:
                return indicators

    return indicators


if __name__ == "__main__":
    print("Connecting to AlienVault OTX...")

    try:
        records = fetch_otx_indicators()

        print(f"Retrieved {len(records)} indicators.")

        for record in records[:10]:
            print(
                f"{record['indicator_type']}: "
                f"{record['indicator_value']} "
                f"| Pulse: {record['pulse_name']}"
            )

    except (requests.RequestException, ValueError, RuntimeError) as error:
        print(f"Collection failed: {error}")
        raise SystemExit(1)
