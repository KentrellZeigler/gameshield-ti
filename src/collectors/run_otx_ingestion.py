
from src.collectors.otx_collector import fetch_otx_indicators
from src.database.ingestion import save_indicators


def main():
    print("Starting GameShield TI intelligence ingestion...")

    indicators = fetch_otx_indicators()

    print(f"Retrieved {len(indicators)} indicators from OTX.")

    if not indicators:
        print("No indicators found. Nothing to save.")
        return

    inserted = save_indicators(indicators)

    print(f"New indicators saved: {inserted}")
    print(f"Existing indicators skipped: {len(indicators) - inserted}")
    print("Ingestion completed successfully.")


if __name__ == "__main__":
    main()
