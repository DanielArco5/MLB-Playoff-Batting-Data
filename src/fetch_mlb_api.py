"""Download postseason team hitting totals from the public MLB Stats API.
One request per season; the raw response is saved untouched in data/raw/mlb_api/.
Seasons already on disk are skipped (pass --force to re-download).
By default only the seasons the build needs (config.MLB_API_YEARS) are fetched; pass --all to
fetch every season from START_YEAR to END_YEAR, which compare_sources.py uses to audit Lahman."""
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

URL = ("https://statsapi.mlb.com/api/v1/teams/stats"
       "?season={year}&sportIds=1&group=hitting&stats=season&gameType=P")


def main():
    force = "--force" in sys.argv
    C.MLB_API_DIR.mkdir(parents=True, exist_ok=True)
    years = C.MLB_API_YEARS
    if "--all" in sys.argv:
        years = [y for y in range(C.START_YEAR, C.END_YEAR + 1) if y not in C.NO_POSTSEASON_YEARS]
    for year in years:
        path = C.mlb_api_file(year)
        if path.exists() and not force:
            print(f"{year}: already saved, skipping")
            continue
        req = urllib.request.Request(URL.format(year=year), headers={"User-Agent": "playoff-ops-skyline/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            path.write_bytes(resp.read())
        print(f"{year}: saved {path.relative_to(C.ROOT)}")
        time.sleep(1)


if __name__ == "__main__":
    main()
