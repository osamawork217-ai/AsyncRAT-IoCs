import os
import sys
import requests

URL = "https://mb-api.abuse.ch/api/v1/"
OUTPUT_FILE = "Malware_Bazaar_Recent.txt"


def fetch_hashes(limit=1000):
    api_key = os.getenv("MB_API_KEY")
    if not api_key:
        raise ValueError("MB_API_KEY environment variable is not set")

    print(f"[DEBUG] API key present: yes")
    print(f"[DEBUG] API key length: {len(api_key)}")

    headers = {
        "API-KEY": api_key,
        "User-Agent": "GitHubActions-MalwareBazaar-Hash-Fetcher/1.0",
    }

    data = {
        "query": "get_recent",
    }

    response = requests.post(URL, data=data, headers=headers, timeout=60)

    print(f"[DEBUG] HTTP status: {response.status_code}")
    print(f"[DEBUG] Response preview: {response.text[:300]}")

    response.raise_for_status()

    json_data = response.json()
    hashes = set()

    query_status = json_data.get("query_status")
    print(f"[DEBUG] query_status: {query_status}")

    if query_status != "ok":
        raise RuntimeError(f"Unexpected API response: {json_data}")

    for sample in json_data.get("data", []):
        sha256 = sample.get("sha256_hash")
        if sha256 and len(sha256) == 64:
            hashes.add(sha256)

    result = sorted(hashes)[:limit]
    print(f"[DEBUG] Valid SHA256 hashes collected: {len(result)}")
    return result


def save_hashes(hashes):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for h in hashes:
            f.write(h + "\n")
    print(f"[DEBUG] Wrote {len(hashes)} hashes to {OUTPUT_FILE}")


if __name__ == "__main__":
    try:
        hashes = fetch_hashes(limit=1000)
        save_hashes(hashes)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        raise
