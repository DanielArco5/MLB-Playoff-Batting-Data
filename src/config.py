"""Shared settings for the Playoff OPS Skyline pipeline and views."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
REF = ROOT / "data" / "ref"
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "out"
CAMPAIGNS_CSV = PROCESSED / "campaigns.csv"

# MLB Stats API postseason team hitting, one saved response per season (src/fetch_mlb_api.py)
MLB_API_DIR = RAW / "mlb_api"
MLB_API_YEARS = [2023, 2024, 2025, 2026]
RESULTS = ["WC", "DS", "CS", "WS-L", "WS-W"]


def mlb_api_file(year: int) -> Path:
    return MLB_API_DIR / f"team_hitting_postseason_{year}.json"

START_YEAR = 1977
END_YEAR = 2026
LAHMAN_END_YEAR = 2025  # last season in the Lahman CSVs; later seasons come from the MLB Stats API
NO_POSTSEASON_YEARS = {1994}  # strike; does not break a streak

LEAGUES = {"AL", "NL"}
CLE_FRANCH_ID = "CLE"
LONG_STREAK = 4
MIN_PA = 0  # views may dim/filter campaigns below this (try 60)
# A campaign needs this many games to be ranked. 8 keeps every World Series team
# (10 would drop three champions from the best-of-five LCS era: 1983 BAL, 1984 DET, 1989 OAK).
MIN_G = 8
MIN_AB_PER_G = 25  # below this, a team-series in BattingPost is missing rows

# Expected number of postseason teams per year (spec format table)
def expected_teams(year: int) -> int:
    if year in NO_POSTSEASON_YEARS:
        return 0
    if year == 1981:
        return 8
    if year <= 1993:
        return 4
    if year <= 2011:
        return 8
    if year <= 2019:
        return 10
    if year == 2020:
        return 16
    if year == 2021:
        return 10
    return 12

OPS_TOLERANCE = 0.002  # vs the outside source in data/ref/spot_checks.csv
MIN_SPOT_CHECKS = 7    # spot checks pass when at least this many are filled and all filled ones agree
