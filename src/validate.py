"""Sanity checks on data/processed/campaigns.csv. Must pass before any chart is built.
Exit code 0 = all checks pass; 1 = something failed or too few spot checks are filled."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
from build_campaigns import apply_series_corrections

results = []  # (name, status, detail) with status in PASS / FAIL / PENDING


def check(name, ok, detail=""):
    results.append((name, "PASS" if ok else "FAIL", detail))


def main():
    df = pd.read_csv(C.CAMPAIGNS_CSV)

    # 1. Row count per year
    counts = df.groupby("year").size()
    bad = []
    for y in range(C.START_YEAR, C.END_YEAR + 1):
        exp, got = C.expected_teams(y), int(counts.get(y, 0))
        if exp != got:
            bad.append(f"{y}: expected {exp}, got {got}")
    check("Row count per year matches format table", not bad, "; ".join(bad))

    # 2. Duplicates
    d = df[df.duplicated(["year", "team_id"], keep=False)]
    check("No duplicate (year, team_id)", d.empty, d[["year", "team_id"]].to_string(index=False) if len(d) else "")

    # 3. Row-level sanity
    bad_pa = df[df["PA"] <= 0]
    check("Every row has PA > 0", bad_pa.empty, f"{len(bad_pa)} rows")
    q = df[df["qualified"]]
    bad_ops = q[(q["OPS"] <= 0.3) | (q["OPS"] >= 1.2)]
    check(f"Every qualified row (G >= {C.MIN_G}) has 0.3 < OPS < 1.2", bad_ops.empty,
          ", ".join(f"{r.year} {r.team_id} {r.OPS:.3f}" for r in bad_ops.itertuples()))
    bad_ll = df[df["lat"].isna() | df["lon"].isna()]
    check("No null lat/lon", bad_ll.empty,
          ", ".join(f"{r.year} {r.team_id}" for r in bad_ll.itertuples()))

    # 4. Exactly one champion per year
    ws = df[df["result"] == "WS-W"].groupby("year").size()
    bad_ws = [y for y in counts.index if ws.get(y, 0) != 1]
    check("Every year has exactly one WS-W", not bad_ws, ", ".join(map(str, bad_ws)))
    bad_res = df[~df["result"].isin(C.RESULTS)]
    check("Every row has a result (WC, DS, CS, WS-L, WS-W)", bad_res.empty,
          ", ".join(f"{r.year} {r.team_id}" for r in bad_res.itertuples())
          + "  (fill in data/ref/results_manual.csv)")

    # 5. Raw completeness: at-bats per game for every team-series
    bat = pd.read_csv(C.RAW / "BattingPost.csv", encoding="utf-8-sig")
    ser = pd.read_csv(C.RAW / "SeriesPost.csv", encoding="utf-8-sig")
    ser = apply_series_corrections(ser[(ser["yearID"] >= C.START_YEAR) & (ser["yearID"] <= C.END_YEAR)])
    ab = bat.groupby(["yearID", "round", "teamID"])["AB"].sum()
    ov = pd.read_csv(C.REF / "mlb_api_overrides.csv")
    overridden = set(zip(ov["year"], ov["team_id"]))
    src = df.set_index(["year", "team_id"])["source"]
    not_applied = [f"{y} {t}" for y, t in overridden if src.get((y, t)) != "mlb_api"]
    thin = [f"override not applied: {x}" for x in not_applied]
    for r in ser.itertuples():
        g = r.wins + r.losses + (0 if pd.isna(r.ties) else r.ties)
        for t in (r.teamIDwinner, r.teamIDloser):
            n = ab.get((r.yearID, r.round, t), 0)
            if (r.yearID, t) in overridden:
                continue  # incomplete in Lahman; campaign uses MLB API totals instead
            if n / g < C.MIN_AB_PER_G:
                thin.append(f"{r.yearID} {r.round} {t}: {n} AB in {int(g)} G ({n / g:.1f}/G)")
    check(f"Every team-series has >= {C.MIN_AB_PER_G} AB per game in BattingPost "
          f"({len(overridden)} campaigns overridden from MLB API)", not thin, "\n".join(thin))

    # 6. Spot checks vs an outside source (check_ops, check_source in spot_checks.csv)
    sc = pd.read_csv(C.REF / "spot_checks.csv")[["year", "team_id", "check_ops", "check_source"]]
    sc = sc.merge(df[["year", "team_id", "OPS", "is_cle"]], on=["year", "team_id"], how="left")
    lines, n_fail, n_pending = [], 0, 0
    for r in sc.itertuples():
        ours = "missing" if pd.isna(r.OPS) else f"{r.OPS:.3f}"
        if pd.isna(r.check_ops):
            n_pending += 1
            lines.append(f"    {r.year} {r.team_id:<4} ours {ours}  check ----   unchecked")
        else:
            ok = not pd.isna(r.OPS) and abs(r.OPS - r.check_ops) <= C.OPS_TOLERANCE + 1e-9
            n_fail += not ok
            lines.append(f"    {r.year} {r.team_id:<4} ours {ours}  check {r.check_ops:.3f}  "
                         f"{'ok' if ok else 'MISMATCH'}  ({r.check_source})")
    n_cle = int(sc["is_cle"].fillna(False).sum())
    structure_ok = len(sc) >= 10 and n_cle >= 3
    n_filled = len(sc) - n_pending
    if n_fail or not structure_ok:
        status = "FAIL"
    elif n_filled < C.MIN_SPOT_CHECKS:
        status = "PENDING"
    else:
        status = "PASS"
    spot_lines = lines
    results.append((f"Spot checks (±{C.OPS_TOLERANCE}): {n_filled} of {len(sc)} checked, {n_filled - n_fail} agree, "
                    f"{n_cle} CLE listed; needs {C.MIN_SPOT_CHECKS}+ checked and all agreeing", status,
                    f"{n_pending} unchecked in data/ref/spot_checks.csv\n" + "\n".join(lines)))

    # Report
    print("VALIDATION")
    for name, status, detail in results:
        print(f"  [{status:^7}] {name}")
        if detail and status != "PASS":
            print("            " + detail.replace("\n", "\n            "))

    cle = df[df["is_cle"]].sort_values("rank_all")
    cq = q[q["is_cle"]].sort_values("rank_qual")
    print("\nSUMMARY")
    print(f"  Window:                 {C.START_YEAR}-{C.END_YEAR} ({df['year'].nunique()} postseasons)")
    print(f"  Total campaigns:        {len(df)}")
    print(f"  Cleveland campaigns:    {len(cle)}  ({', '.join(map(str, sorted(cle['year'])))})")
    if len(cle):
        b, w = cle.iloc[0], cle.iloc[-1]
        print(f"  Cleveland best rank:    #{b.rank_all} of {len(df)}  ({b.year}, OPS {b.OPS:.3f}, {b.result})")
        print(f"  Cleveland worst rank:   #{w.rank_all} of {len(df)}  ({w.year}, OPS {w.OPS:.3f}, {w.result})")
    print(f"  in_long_streak rows:    {int(df['in_long_streak'].sum())}")
    print(f"  Source:                 {int((df['source'] == 'lahman').sum())} Lahman, "
          f"{int((df['source'] == 'mlb_api').sum())} MLB Stats API")
    print("\nSPOT CHECKS")
    print("\n".join(spot_lines))
    print(f"\nQUALIFIED (G >= {C.MIN_G}, each campaign counts once)")
    print(f"  Qualified campaigns:    {len(q)} of {len(df)}")
    print(f"  Cleveland qualified:    {len(cq)}")
    for r in cq.itertuples():
        print(f"    #{int(r.rank_qual):>3} of {len(q)}  {r.year}  OPS {r.OPS:.3f}  {r.G} G  {r.result}")

    print("\nTEAMS PER YEAR (got / expected)")
    flags = {1981: "split season, extra division round", 1994: "strike, no postseason",
             2020: "16-team expanded format"}
    cells = []
    for y in range(C.START_YEAR, C.END_YEAR + 1):
        got, exp = int(counts.get(y, 0)), C.expected_teams(y)
        mark = "" if got == exp else "  <-- MISMATCH"
        if y in flags:
            mark += f"  <-- {flags[y]}" + (" (absent, as expected)" if y == 1994 and got == 0 else "")
            cells.append(None)
            print(f"  {y}: {got:>2} / {exp:<2}{mark}")
    plain = [y for y in range(C.START_YEAR, C.END_YEAR + 1) if y not in flags]
    for i in range(0, len(plain), 8):
        print("  " + "   ".join(f"{y}:{int(counts.get(y, 0)):>2}/{C.expected_teams(y):<2}" for y in plain[i:i + 8]))

    statuses = {s for _, s, _ in results}
    verdict = "FAIL" if "FAIL" in statuses else "PENDING" if "PENDING" in statuses else "PASS"
    print(f"\nRESULT: {verdict}" + (" (fill check_ops in data/ref/spot_checks.csv)" if verdict == "PENDING" else ""))
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
