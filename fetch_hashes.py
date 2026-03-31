import requests

URL = "https://mb-api.abuse.ch/api/v1/"
OUTPUT_FILE = "Malware_Bazaar_Recent.txt"

def fetch_hashes(limit=1000):
    data = {
        "query": "get_recent"
    }

    response = requests.post(URL, data=data)
    response.raise_for_status()

    json_data = response.json()
    hashes = set()

    if json_data["query_status"] == "ok":
        for sample in json_data["data"]:
            sha256 = sample.get("sha256_hash")
            if sha256 and len(sha256) == 64:
                hashes.add(sha256)

    return sorted(hashes)


def save_hashes(hashes):
    with open(OUTPUT_FILE, "w") as f:
        for h in hashes:
            f.write(h + "\n")


if __name__ == "__main__":
    hashes = fetch_hashes()
    save_hashes(hashes)
