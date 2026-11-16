"""Two independent checks against the saved MLB Stats API responses (run fetch_mlb_api.py --all first):
1. Lahman's BattingPost.csv, summed per team, against the API for every season both cover.
2. The finished campaigns.csv (games, PA, OPS) against the API for every campaign.
Prints each difference."""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
import build_campaigns as B

STATS = ["AB", "R", "H", "2B", "3B", "HR", "BB", "HBP", "SF", "SH", "SO"]


def main():
    bat, _, teams = B.load()
    lah = B.aggregate_batting(bat).rename(columns={"yearID": "year", "teamID": "team_id"})
    lah["OPS"] = B.slash(lah)["OPS"]
    # Team codes differ between the sources for relocated or renamed clubs (CAL/LAA, OAK/ATH, MON/WAS...),
    # so the two are matched on season + franchise instead.
    franch = teams.rename(columns={"yearID": "year", "teamID": "team_id", "franchID": "franch_id"})[["year", "team_id", "franch_id"]]
    lah = lah.merge(franch, on=["year", "team_id"], how="left")
    # every season that has a saved API response and is covered by Lahman
    years = [y for y in range(C.START_YEAR, C.LAHMAN_END_YEAR + 1) if C.mlb_api_file(y).exists()]
    api = pd.concat([B.load_mlb_api(y) for y in years])
    api["OPS"] = B.slash(api)["OPS"]
    m = lah[lah["year"].isin(years)].merge(api, on=["year", "franch_id"], how="outer",
                                           suffixes=("_lahman", "_api"), indicator=True)
    unmatched = m[m["_merge"] != "both"]
    exact = 0
    for r in m[m["_merge"] == "both"].itertuples():
        diffs = []
        for s in STATS:
            a, b = m.at[r.Index, f"{s}_lahman"], m.at[r.Index, f"{s}_api"]
            if a != b:
                diffs.append(f"{s} {int(a)} vs {int(b)}")
        if diffs:
            print(f"  {r.year} {r.franch_id}: Lahman vs API: {', '.join(diffs)}; "
                  f"OPS {r.OPS_lahman:.3f} vs {r.OPS_api:.3f}")
        else:
            exact += 1
    n = int((m["_merge"] == "both").sum())
    print(f"{exact} of {n} team-seasons ({years[0]}-{years[-1]}) match on every counting stat; "
          f"{len(unmatched)} teams appear in only one source")
    audit_campaigns()


def audit_campaigns():
    """campaigns.csv against the API's own games, plate appearances and OPS, campaign by campaign."""
    df = pd.read_csv(C.CAMPAIGNS_CSV)
    ids = pd.read_csv(C.REF / "team_id_map.csv").set_index("mlb_id")["franch_id"]
    checked, games, ops, pa, missing = 0, [], [], [], []
    for year, rows in df.groupby("year"):
        if not C.mlb_api_file(year).exists():
            missing.append(int(year))
            continue
        api = {ids[s["team"]["id"]]: s["stat"]
               for s in json.loads(C.mlb_api_file(year).read_text())["stats"][0]["splits"]}
        if set(api) != set(rows["franch_id"]):
            print(f"  {year}: team lists differ: {sorted(set(api) ^ set(rows['franch_id']))}")
        for r in rows.itertuples():
            a = api.get(r.franch_id)
            if a is None:
                continue
            checked += 1
            tag = f"{r.year} {r.franch_id}"
            if int(a["gamesPlayed"]) != r.G:
                games.append(f"{tag} {r.G} vs {a['gamesPlayed']}")
            if abs(float(a["ops"]) - r.OPS) > 0.0015:
                ops.append(f"{tag} {r.OPS:.3f} vs {a['ops']}")
            if int(a["plateAppearances"]) != r.PA:
                pa.append(f"{tag} {r.PA} vs {a['plateAppearances']}")
    print(f"campaigns.csv vs API: {checked} of {len(df)} campaigns checked"
          + (f" (no saved response for {missing})" if missing else ""))
    print(f"  games differ: {len(games)} {games}")
    print(f"  OPS differs by more than .0015: {len(ops)} {ops}")
    print(f"  PA differs: {len(pa)} (the API counts something our AB+BB+HBP+SF+SH does not, "
          f"probably catcher's interference; OPS is unaffected) {pa}")


if __name__ == "__main__":
    main()
