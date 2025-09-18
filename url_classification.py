from urllib.parse import urlparse
import sys


def classify_url(url: str) -> str:
    parsed = urlparse(url)
    domain, path = parsed.netloc, parsed.path.lower()

    if "huggingface.co" in domain:
        if path.startswith("/datasets/"):
            return "DATASET"
        else:
            return "MODEL"
    elif "github.com" in domain:
        return "CODE"
    else:
        return "UNKNOWN"


def main():
    if len(sys.argv) != 2:
        print("Usage: python classify.py <URL_FILE>")
        sys.exit(1)

    url_file = sys.argv[1]

    try:
        with open(url_file, "r") as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{url_file}' not found.")
        sys.exit(1)

    for url in urls:
        print(url, "->", classify_url(url))


if __name__ == "__main__":
    main()
