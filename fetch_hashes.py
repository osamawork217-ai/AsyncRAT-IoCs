import os
import sys
import requests

URL = "https://mb-api.abuse.ch/api/v1/"
OUTPUT_FILE = "Malware_Bazaar_Recent.txt"


def fetch_hashes(limit=100):
    api_key = os.getenv("MB_API_KEY")
    if not api_key:
        raise ValueError("MB_API_KEY environment variable is not set")

    print("[DEBUG] API key present: yes")
    print(f"[DEBUG] API key length: {len(api_key)}")

    headers = {
        "Auth-Key": api_key,
        "User-Agent": "GitHubActions-MalwareBazaar-Hash-Fetcher/1.0",
    }

    data = {
        "query": "get_recent",
        "selector": "100",
    }

    response = requests.post(URL, data=data, headers=headers, timeout=60)

    print(f"[DEBUG] HTTP status: {response.status_code}")
    print(f"[DEBUG] Response preview: {response.text[:300]}")

    response.raise_for_status()

    json_data = response.json()
    query_status = json_data.get("query_status")
    print(f"[DEBUG] query_status: {query_status}")

    if query_status not in {"ok", "no_results"}:
        raise RuntimeError(f"Unexpected API response: {json_data}")

    hashes = []
    for sample in json_data.get("data", []):
        sha256 = sample.get("sha256_hash")
        if sha256 and len(sha256) == 64:
            hashes.append(sha256)

    print(f"[DEBUG] Valid SHA256 hashes collected from API: {len(hashes)}")
    return hashes[:limit]


def load_existing_hashes():
    if not os.path.exists(OUTPUT_FILE):
        return []

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def save_hashes(new_hashes, max_hashes=10000):
    existing_hashes = load_existing_hashes()

    # Preserve recency order:
    # older existing hashes first, newest API hashes appended at the end
    combined = existing_hashes + list(new_hashes)

    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for h in combined:
        if h not in seen:
            seen.add(h)
            unique.append(h)

    # Keep only the most recent max_hashes
    if len(unique) > max_hashes:
        unique = unique[-max_hashes:]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for h in unique:
            f.write(h + "\n")

    print(f"[DEBUG] Existing hashes: {len(existing_hashes)}")
    print(f"[DEBUG] New hashes from API: {len(new_hashes)}")
    print(f"[DEBUG] Total hashes after merge (capped): {len(unique)}")
    print(f"[DEBUG] Wrote merged hashes to {OUTPUT_FILE}")


if __name__ == "__main__":
    try:
        hashes = fetch_hashes(limit=100)
        save_hashes(hashes, max_hashes=10000)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        raise
