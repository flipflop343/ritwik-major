"""Download the UCI SMS Spam Collection (CC BY 4.0) into data/raw/.

Run from the backend folder:  python -m ml.download_data
"""
import io
import urllib.request
import zipfile
from pathlib import Path

URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    target = RAW_DIR / "SMSSpamCollection"
    if target.exists():
        print(f"Already present: {target}")
        return
    print(f"Downloading {URL} ...")
    with urllib.request.urlopen(URL, timeout=60) as resp:
        data = resp.read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        target.write_bytes(z.read("SMSSpamCollection"))
    print(f"Saved {target}")


if __name__ == "__main__":
    main()
