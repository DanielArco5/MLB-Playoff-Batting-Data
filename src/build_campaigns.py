"""raw Lahman CSVs -> data/processed/campaigns.csv  (see docs/02_DATA_PIPELINE.md)"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

COUNT_COLS = ["AB", "R", "H", "2B", "3B", "HR", "BB", "HBP", "SF", "SO", "SH"]
ROUND_RANK = {"WC": 1, "DS": 2, "CS": 3, "WS": 4}


def round_level(rnd: str) -> str:
    """Map Lahman SeriesPost round codes to WC/DS/CS/WS."""
    if rnd == "WS":
        return "WS"
    if rnd.endswith("CS"):
        return "CS"
    if "WC" in rnd:
        return "WC"
    if "DS" in rnd or rnd.endswith("DIV"):  # ALDS1, NLDS2, 1981 AEDIV/AWDIV/NEDIV/NWDIV
        return "DS"
    raise ValueError(f"Unknown postseason round code: {rnd!r}")


def slash(df: pd.DataFrame) -> pd.DataFrame:
    """BA/OBP/SLG/OPS from summed counting stats (spec formula)."""
    singles = df["H"] - df["2B"] - df["3B"] - df["HR"]
    tb = singles + 2 * df["2B"] + 3 * df["3B"] + 4 * df["HR"]
    out = pd.DataFrame(index=df.index)
    out["BA"] = df["H"] / df["AB"]
    out["OBP"] = (df["H"] + df["BB"] + df["HBP"]) / (df["AB"] + df["BB"] + df["HBP"] + df["SF"])
    out["SLG"] = tb / df["AB"]
    out["OPS"] = out["OBP"] + out["SLG"]
    return out


def apply_series_corrections(ser: pd.DataFrame) -> pd.DataFrame:
    """Overwrite wins/losses for series listed in data/ref/series_corrections.csv."""
    path = C.REF / "series_corrections.csv"
    if not path.exists():
        return ser
    ser = ser.copy()
    for fix in pd.read_csv(path).itertuples():
        hit = (ser["yearID"] == fix.yearID) & (ser["round"] == fix.round)
        if hit.sum() != 1:
            raise ValueError(f"series_corrections.csv: {fix.yearID} {fix.round} matches {hit.sum()} series")
        ser.loc[hit, ["wins", "losses"]] = [fix.wins, fix.losses]
    return ser


def load():
    bat = pd.read_csv(C.RAW / "BattingPost.csv", encoding="utf-8-sig")
    ser = pd.read_csv(C.RAW / "SeriesPost.csv", encoding="utf-8-sig")
    teams = pd.read_csv(C.RAW / "Teams.csv", encoding="utf-8-sig")
    last = min(C.END_YEAR, C.LAHMAN_END_YEAR)
    in_window = lambda d: d[(d["yearID"] >= C.START_YEAR) & (d["yearID"] <= last)]
    return in_window(bat), apply_series_corrections(in_window(ser)), in_window(teams)


def aggregate_batting(bat: pd.DataFrame) -> pd.DataFrame:
    bat = bat[bat["lgID"].isin(C.LEAGUES)].copy()
    bat[COUNT_COLS] = bat[COUNT_COLS].fillna(0).astype(int)  # old rows have blank HBP/SF/SH
    agg = bat.groupby(["yearID", "teamID"], as_index=False)[COUNT_COLS].sum()
    agg["PA"] = agg["AB"] + agg["BB"] + agg["HBP"] + agg["SF"] + agg["SH"]
    return agg


def series_results(ser: pd.DataFrame) -> pd.DataFrame:
    """Games played and furthest round reached per (year, team)."""
    ser = ser.copy()
    ser["level"] = ser["round"].map(round_level)
    ser["games"] = ser["wins"] + ser["losses"] + ser["ties"].fillna(0)
    w = ser.rename(columns={"teamIDwinner": "teamID"}).assign(won=True)
    l = ser.rename(columns={"teamIDloser": "teamID"}).assign(won=False)
    long = pd.concat([w, l])[["yearID", "teamID", "level", "games", "won"]]
    long["lvl_rank"] = long["level"].map(ROUND_RANK)

    games = long.groupby(["yearID", "teamID"], as_index=False)["games"].sum().rename(columns={"games": "G"})
    furthest = long.sort_values("lvl_rank").groupby(["yearID", "teamID"]).tail(1)
    furthest["result"] = np.where(
        furthest["level"] == "WS",
        np.where(furthest["won"], "WS-W", "WS-L"),
        furthest["level"],
    )
    return games.merge(furthest[["yearID", "teamID", "result"]], on=["yearID", "teamID"])


API_FIELDS = {"gamesPlayed": "G", "atBats": "AB", "runs": "R", "hits": "H", "doubles": "2B", "triples": "3B",
              "homeRuns": "HR", "baseOnBalls": "BB", "hitByPitch": "HBP", "sacFlies": "SF", "strikeOuts": "SO",
              "sacBunts": "SH"}


def load_mlb_api(year: int) -> pd.DataFrame:
    """One season of postseason team hitting from the saved MLB Stats API response,
    with Lahman column names and team IDs (via data/ref/team_id_map.csv)."""
    splits = json.loads(C.mlb_api_file(year).read_text())["stats"][0]["splits"]
    rows = [{"year": year, "mlb_id": s["team"]["id"], "team_name": s["team"]["name"],
             **{ours: int(s["stat"][theirs]) for theirs, ours in API_FIELDS.items()}} for s in splits]
    df = pd.DataFrame(rows).merge(pd.read_csv(C.REF / "team_id_map.csv"), on="mlb_id", how="left")
    if df["team_id"].isna().any():
        raise ValueError(f"MLB team ids missing from team_id_map.csv: {df[df['team_id'].isna()]['mlb_id'].tolist()}")
    return df.drop(columns="mlb_id")


def apply_api_overrides(df: pd.DataFrame) -> pd.DataFrame:
    """Replace counting stats with MLB API totals for campaigns in data/ref/mlb_api_overrides.csv."""
    df = df.copy()
    for o in pd.read_csv(C.REF / "mlb_api_overrides.csv").itertuples():
        api = load_mlb_api(o.year).set_index("team_id").loc[o.team_id]
        hit = (df["year"] == o.year) & (df["team_id"] == o.team_id)
        if hit.sum() != 1:
            raise ValueError(f"mlb_api_overrides.csv: {o.year} {o.team_id} matches {hit.sum()} campaigns")
        if int(df.loc[hit, "G"].iat[0]) != int(api["G"]):
            raise ValueError(f"{o.year} {o.team_id}: games differ (SeriesPost {df.loc[hit, 'G'].iat[0]}, API {api['G']})")
        df.loc[hit, COUNT_COLS] = [int(api[c]) for c in COUNT_COLS]
        df.loc[hit, "source"] = "mlb_api"
    return df


def api_seasons() -> pd.DataFrame:
    """Campaigns for seasons after Lahman ends. Results come from data/ref/results_manual.csv."""
    years = range(C.LAHMAN_END_YEAR + 1, C.END_YEAR + 1)
    if not years:
        return pd.DataFrame()
    df = pd.concat([load_mlb_api(y) for y in years])
    manual = pd.read_csv(C.REF / "results_manual.csv")[["year", "team_id", "result"]]
    df = df.merge(manual, on=["year", "team_id"], how="left")
    df["source"] = "mlb_api"
    return df


def add_streaks(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["franch_id", "year"]).copy()
    run_ids = []
    for _, g in df.groupby("franch_id", sort=False):
        run, prev = 0, None
        for y in g["year"]:
            consecutive = prev is not None and (
                y - prev == 1 or (prev == 1993 and y == 1995)  # 1994 had no postseason
            )
            if not consecutive:
                run += 1
            run_ids.append(f"{g['franch_id'].iat[0]}-{run}")
            prev = y
    df["_run"] = run_ids
    df["streak_len"] = df.groupby("_run")["year"].transform("size").astype(int)
    df["in_long_streak"] = df["streak_len"] >= C.LONG_STREAK
    return df.drop(columns="_run")


def add_coords(df: pd.DataFrame) -> pd.DataFrame:
    parks = pd.read_csv(C.REF / "ballparks.csv")
    m = df[["year", "team_id"]].merge(parks, on="team_id", how="left")
    m = m[(m["year"] >= m["from_year"]) & (m["year"] <= m["to_year"])]
    dupes = m.duplicated(["year", "team_id"], keep=False)
    if dupes.any():
        raise ValueError(f"Overlapping ballpark ranges:\n{m[dupes]}")
    return df.merge(m[["year", "team_id", "park", "lat", "lon"]], on=["year", "team_id"], how="left")


def main():
    bat, ser, teams = load()
    df = aggregate_batting(bat).merge(series_results(ser), on=["yearID", "teamID"], how="left")

    t = teams[["yearID", "teamID", "franchID", "name", "lgID"]]
    df = df.merge(t, on=["yearID", "teamID"], how="left", validate="one_to_one")
    missing = df[df["franchID"].isna() | df["result"].isna()]
    if len(missing):
        raise ValueError(f"Batting rows with no Teams/SeriesPost match:\n{missing[['yearID','teamID']]}")

    df = df.rename(columns={"yearID": "year", "teamID": "team_id", "franchID": "franch_id",
                            "name": "team_name", "lgID": "league"})
    df["source"] = "lahman"
    df = apply_api_overrides(df)
    df = pd.concat([df, api_seasons()], ignore_index=True)
    df[["G"] + COUNT_COLS] = df[["G"] + COUNT_COLS].astype(int)
    df["PA"] = df["AB"] + df["BB"] + df["HBP"] + df["SF"] + df["SH"]
    df = pd.concat([df, slash(df)], axis=1)
    df["R_per_G"] = df["R"] / df["G"]

    # Postseason average: PA-weighted by summing every team's counting stats that year
    yr = df.groupby("year")[COUNT_COLS].sum()
    ps_avg = slash(yr)["OPS"].rename("ps_avg_OPS")
    df = df.merge(ps_avg, left_on="year", right_index=True)
    df["OPS_vs_avg"] = df["OPS"] - df["ps_avg_OPS"]

    df["rank_all"] = df["OPS"].rank(ascending=False, method="min").astype(int)
    # Every qualified campaign counts once (no PA weighting); short ones are kept but unranked
    df["qualified"] = df["G"] >= C.MIN_G
    df["rank_qual"] = df.loc[df["qualified"], "OPS"].rank(ascending=False, method="min").astype("Int64")
    df["rank_qual"] = df["rank_qual"].astype("Int64")
    df["is_cle"] = df["franch_id"] == C.CLE_FRANCH_ID
    df = add_streaks(df)
    df = add_coords(df)

    for col in ["BA", "OBP", "SLG", "OPS", "ps_avg_OPS", "OPS_vs_avg"]:
        df[col] = df[col].round(3)
    df["R_per_G"] = df["R_per_G"].round(2)

    cols = ["year", "team_id", "franch_id", "team_name", "league", "result",
            "G", "PA", "AB", "R", "H", "2B", "3B", "HR", "BB", "HBP", "SF", "SO", "SH",
            "BA", "OBP", "SLG", "OPS", "R_per_G", "ps_avg_OPS", "OPS_vs_avg", "rank_all", "qualified", "rank_qual",
            "streak_len", "in_long_streak", "is_cle", "park", "lat", "lon", "source"]
    df = df[cols].sort_values(["year", "OPS"], ascending=[True, False])

    C.PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(C.CAMPAIGNS_CSV, index=False)
    print(f"Wrote {len(df)} campaigns ({C.START_YEAR}-{C.END_YEAR}), {int(df['qualified'].sum())} with G >= {C.MIN_G} "
          f"-> {C.CAMPAIGNS_CSV.relative_to(C.ROOT)}")


if __name__ == "__main__":
    main()
