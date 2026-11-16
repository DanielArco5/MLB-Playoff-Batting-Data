# 02 — Data Pipeline

Goal: one clean `data/processed/campaigns.csv` with ~374 rows (see the spec).

## Sources (A is the base, B fills the gaps, C is for checking)

### A. Lahman Baseball Database (recommended: free, no scraping, OK to publish)
- Download the CSV version from **seanlahman.com** (Baseball Databank). You need:
  - `BattingPost.csv`: player batting for each postseason round
  - `SeriesPost.csv`: who won and lost each series (gives `result`)
  - `Teams.csv`: team names and `franchID` for each season
- License: CC BY-SA 3.0. Credit it on your pages.
- **Coverage:** the copy in `data/raw/` runs through **2025** (`LAHMAN_END_YEAR` in `src/config.py`). 2026 comes from source B.
- **Known gap:** `BattingPost.csv` has only about half the at-bats for two 2023 series, Houston–Minnesota (ALDS) and Texas–Houston (ALCS). The 2023 Rangers, Astros and Twins are therefore overridden from source B.
- **Known error:** `SeriesPost.csv` lists the 2013 World Series as 4–3. Boston won 4–2. Fixed through `data/ref/series_corrections.csv`.
- Gotcha: **OBP needs HBP and SF**. Both are in BattingPost, but some old rows have blanks. Treat blank as 0.

### B. MLB Stats API (fills what Lahman lacks)
The public MLB Stats API returns postseason team hitting totals for a whole season in one request:

```
https://statsapi.mlb.com/api/v1/teams/stats?season=<year>&sportIds=1&group=hitting&stats=season&gameType=P
```

- `src/fetch_mlb_api.py` makes **one request per season** (2023–2026) and saves each response untouched as `data/raw/mlb_api/team_hitting_postseason_<year>.json`. Seasons already saved are skipped.
- It is used for two things only:
  1. **Overrides:** campaigns listed in `data/ref/mlb_api_overrides.csv` (2023 TEX, HOU, MIN and 2024 CLE) take their counting stats from the API. Games, result and team name still come from Lahman, and the build stops if the two sources disagree on games played.
  2. **Seasons after Lahman ends:** every 2026 team.
- The API gives games played but not the round reached, so results for those seasons live in `data/ref/results_manual.csv`.
- OPS is still computed from the summed counting stats with the spec formula. The API's own `ops` field is not used. PA is `AB + BB + HBP + SF + SH`, which can be 1 lower than the API's figure when there was a catcher's interference.
- **Proof it agrees with Lahman:** `src/compare_sources.py` compares both sources for 2023–2025. 32 of 36 team-seasons match on every counting stat. Three of the four that differ are the 2023 overrides. The fourth is the 2024 Guardians, where Lahman is one hit short (82 vs 83; OPS .680 vs .685). StatMuse agrees with the API, so that campaign is overridden too.

### C. Baseball-Reference pages (free, manual spot checks only)
Each year's postseason and series pages carry team batting totals. Use them to **spot-check** about 10 campaigns, at human browsing speed.

**Rules that matter:**
- Sports Reference blocks anyone sending more than **20 requests a minute**, and the block can last up to a day.
- Its data-use policy says you shouldn't build websites or tools from data scraped off its sites without permission. That's why **A is the base layer**: your published pages are built on Lahman, and BR is only a check.

## Steps in `src/build_campaigns.py`

1. **Load** `BattingPost`, `SeriesPost`, `Teams` from `data/raw/`.
2. **Filter** to `START_YEAR <= yearID <= END_YEAR`, AL/NL only.
3. **Aggregate** BattingPost per `(yearID, teamID)`. Sum AB, R, H, 2B, 3B, HR, BB, HBP, SF, SO, SH. `G` is counted from SeriesPost (wins + losses + ties), after applying `data/ref/series_corrections.csv`.
   - `PA = AB + BB + HBP + SF + SH`
4. **Compute** BA, OBP, SLG, OPS with the formulas in `01_SPEC.md`.
5. **Join** `Teams` on `(yearID, teamID)` to get `franch_id`, `team_name`, `league`.
6. **Result**: from SeriesPost, the furthest round each team reached that year, plus WS-W/WS-L.
7. **Override and append** from the MLB Stats API files. Replace the counting stats of campaigns in `data/ref/mlb_api_overrides.csv`, then append every team for seasons after `LAHMAN_END_YEAR`, with results from `data/ref/results_manual.csv`. MLB team ids map to Lahman `teamID` through `data/ref/team_id_map.csv`. Each row's `source` column says `lahman` or `mlb_api`.
8. **Postseason average**: per year, sum all teams' counting stats and compute OPS. Gives `ps_avg_OPS` and `OPS_vs_avg`.
9. **Streaks**: per `franch_id`, sort the years. Years `y` and `y_next` are consecutive if `y_next - y == 1`, **or** if `y == 1993` and `y_next == 1995`. Label runs, then compute `streak_len` and `in_long_streak`.
10. **Coordinates**: join `data/ref/ballparks.csv` on `(team_id, year)` ranges to get `lat`/`lon`.
11. `is_cle = franch_id == "CLE"`, `rank_all` by OPS descending, `qualified = G >= MIN_G` (8), `rank_qual` by OPS among qualified campaigns.
12. Write `data/processed/campaigns.csv`.

## Reference tables you make by hand (`data/ref/`)

**`ballparks.csv`**: one row per team per ballpark era. This is about 40 rows, and Claude can draft it for you to check.

| team_id | from_year | to_year | park | lat | lon |
|---|---|---|---|---|---|
| CLE | 1977 | 1993 | Cleveland Stadium | … | … |
| CLE | 1994 | 2026 | Progressive Field | … | … |

Moves to watch: Expos (MON) to Nationals (WAS), Marlins (FLO to MIA), Angels team-ID changes (CAL/ANA/LAA), Rays (TBA). Also note new parks in the same city (doesn't matter much for a globe view).

**`team_id_map.csv`**: MLB Stats API team id to Lahman `teamID`, `franch_id` and league, for all 30 current teams (e.g. `114` to `CLE`, `147` to `NYA`, `133` to `ATH`).

**`mlb_api_overrides.csv`**: campaigns whose counting stats come from the MLB Stats API because Lahman's rows are incomplete, with the reason.

**`results_manual.csv`**: furthest round reached for seasons after Lahman ends. The 2026 rows were derived from games played, which fixes every team except the two World Series teams. Their result was entered by hand: Milwaukee beat Tampa Bay in five games.

**`series_corrections.csv`**: corrected wins and losses for series that are wrong in `SeriesPost.csv`.

**`spot_checks.csv`**: the 10 campaigns checked against an outside source. `check_ops` holds that source's OPS and `check_source` names it (StatMuse so far; Baseball-Reference works too). Seven are filled; the 1977 Yankees, 2014 Giants and 2025 Dodgers are unchecked.

## `src/validate.py` checks (all must pass)

- [ ] Row count per year matches the format table in the spec (1981 = 8, 2020 = 16, 1994 absent)
- [ ] No duplicate `(year, team_id)`
- [ ] Every row has `PA > 0` and non-null `lat`/`lon`. Every qualified row (`G >= MIN_G`) has `0.3 < OPS < 1.2`
- [ ] Every year has exactly one `WS-W`, and every row has a result
- [ ] Every team-series in `BattingPost.csv` has at least 25 AB per game, except campaigns overridden from the MLB Stats API (and each listed override was applied)
- [ ] Spot check: 10 campaigns listed (including 3+ Cleveland) in `data/ref/spot_checks.csv`. Passes when at least 7 have a `check_ops` value and every filled one is within ±.002 of ours
- [ ] Print a summary: total campaigns, Cleveland campaigns, Cleveland's best and worst rank, number of `in_long_streak` campaigns, rows per source, Cleveland's ranks among qualified campaigns, teams per year

## Full-history audit

`python src/fetch_mlb_api.py --all` saves one MLB Stats API response for every season from 1977 (one request per season, skipped if already on disk). `python src/compare_sources.py` then checks two things:

1. Lahman's `BattingPost.csv`, summed per team, against the API for 1977–2025, matched on season and franchise. 358 of 362 team-seasons agree on every counting stat; the other four are the campaigns already overridden in `data/ref/mlb_api_overrides.csv`.
2. The finished `campaigns.csv` against the API's games played, plate appearances and OPS. Games and OPS agree for all 374 campaigns. Plate appearances differ by one in 20 campaigns (the API counts something `AB + BB + HBP + SF + SH` does not, probably catcher's interference); OPS is unaffected.

The build itself still reads the API only for the seasons in `config.MLB_API_YEARS`.
