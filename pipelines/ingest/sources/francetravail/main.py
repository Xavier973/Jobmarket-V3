import argparse
import os
from pathlib import Path
from typing import Any, Dict, List

from pipelines.ingest.io import write_jsonl
from pipelines.ingest.normalizer import normalize_offer
from pipelines.ingest.sources.francetravail.client import FranceTravailClient


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name, str(default)).strip()
    try:
        return int(value)
    except ValueError:
        return default


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def run(sample: bool = False) -> None:
    _load_env_file(Path("config/.env"))
    output_dir = Path(os.getenv("INGEST_OUTPUT_DIR", "./data"))
    max_pages = _int_env("INGEST_MAX_PAGES", 5)
    page_size = _int_env("INGEST_PAGE_SIZE", 50)

    if sample:
        max_pages = 1
        page_size = min(page_size, 5)

    filename = "offers_sample.jsonl" if sample else "offers.jsonl"
    raw_path = output_dir / "raw" / "francetravail" / filename
    normalized_path = output_dir / "normalized" / "francetravail" / filename

    client = FranceTravailClient()

    for page in range(0, max_pages):
        params = {"page": page, "size": page_size}
        payload = client.search_offers(params)
        offers: List[Dict[str, Any]] = payload.get("resultats", [])
        if not offers:
            break

        write_jsonl(raw_path, offers)
        normalized = [normalize_offer(raw, "francetravail").to_dict() for raw in offers]
        write_jsonl(normalized_path, normalized)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="France Travail ingestion")
    parser.add_argument("--sample", action="store_true", help="Fetch a small sample and store in separate files")
    args = parser.parse_args()
    run(sample=args.sample)
