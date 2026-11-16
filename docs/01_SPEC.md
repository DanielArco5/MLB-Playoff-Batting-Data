# 01 — Project Spec

## The question

Across every MLB postseason campaign of the last 50 years, how did each team's offense perform? Specifically:

1. Where do Cleveland's postseason offenses rank all-time in that window?
2. How do they compare with other franchises that made **4+ consecutive postseasons**, teams that kept getting chances just like Cleveland did?

## Scope

| Item | Decision |
|------|----------|
| Years | **1977–2026** (50 seasons). `END_YEAR` lives in `src/config.py` so the window can roll forward |
| Sources | Lahman CSVs for 1977–2025. The public MLB Stats API for all of 2026 and for four campaigns whose Lahman rows are incomplete (2023 Rangers, Astros and Twins; 2024 Guardians). See `02_DATA_PIPELINE.md` |
| Missing year | **1994** had no postseason (strike), so the window holds 49 postseasons |
| Unit of analysis | One **campaign**, meaning one team's entire postseason in one year, all rounds combined |
| Expected size | **374 campaigns** (4 teams a year 1977–93, 8 in 1981, 8 a year 1995–2011, 10 a year 2012–19, 16 in 2020, 10 in 2021, 12 a year 2022–26) |
| Leagues | AL + NL only |
| Metric | **OPS** (on-base + slugging). R/G, BA, OBP and SLG are carried along for tooltips |

## Definitions (fixed)

**Campaign OPS.** Sum every counting stat across all of a team's postseason games that year, then compute:

```
OBP = (H + BB + HBP) / (AB + BB + HBP + SF)
SLG = (1B + 2*2B + 3*3B + 4*HR) / AB        where 1B = H - 2B - 3B - HR
OPS = OBP + SLG
```

Never average OPS across series. A 2-game wild card round and a 7-game World Series have to be weighted by plate appearances, and summing the counting stats does that automatically.

**Franchise.** Uses Lahman `franchID`. Cleveland = `CLE` across the Indians and Guardians names. The Expos and Nationals share `WSN`, the Angels' names share `ANA`, and so on.

**Streak.** A run of consecutive postseason appearances by one franchise. **1994 doesn't break a streak** (no postseason was held), so Atlanta 1991–2005 counts as one 14-appearance run.
- `streak_len`: length of the run this campaign belongs to
- `in_long_streak`: `streak_len >= 4`

**Postseason average.** The PA-weighted OPS of all teams in that year's postseason, computed the same way from summed stats. Used for the optional "vs. that October" mode.

**Games.** `G` is the team's postseason games that year, counted from `SeriesPost.csv` (wins + losses + ties over every series it played). Known errors in that file are fixed through `data/ref/series_corrections.csv` (currently the 2013 World Series, which Boston won 4–2), never by editing the raw file.

**Qualification (games minimum).** A campaign is **qualified** when `G >= MIN_G`. `MIN_G` is **8** in `src/config.py`. Eight keeps every World Series team; ten would drop eight pennant winners from the best-of-five LCS era, including three champions (1983 Orioles, 1984 Tigers, 1989 A's).
- Every qualified campaign counts once in the ranking. There is no weighting by PA or games.
- `rank_qual` ranks qualified campaigns only (1 = best OPS). It is blank for unqualified campaigns.
- Unqualified campaigns stay in the table with `qualified = False`. `rank_all` still ranks every campaign.
- 161 of 374 campaigns qualify, 7 of them Cleveland's.

**Small samples.** Wild card game teams can have about 35 PA. They are kept, but every campaign carries `PA` and `G`, and each view can dim or filter campaigns that are not `qualified` (or are under `MIN_PA`, default 0).

## Output table: `data/processed/campaigns.csv`

| column | type | example |
|---|---|---|
| `year` | int | 2016 |
| `team_id` | str (Lahman teamID) | CLE |
| `franch_id` | str | CLE |
| `team_name` | str (name that season) | Cleveland Indians |
| `league` | AL/NL | AL |
| `result` | str: furthest round reached (WC, DS, CS, WS-L, WS-W). From `SeriesPost.csv` through 2025, from `data/ref/results_manual.csv` after | WS-L |
| `G`, `PA`, `AB`, `R`, `H`, `2B`, `3B`, `HR`, `BB`, `HBP`, `SF`, `SO`, `SH` | int (`PA = AB + BB + HBP + SF + SH`) | |
| `BA`, `OBP`, `SLG`, `OPS` | float, 3 dp | .227 / .292 / .393 / .685 |
| `R_per_G` | float | 3.1 |
| `ps_avg_OPS` | float: that postseason's average OPS | .701 |
| `OPS_vs_avg` | float: `OPS - ps_avg_OPS` | -.016 |
| `rank_all` | int: 1 = best OPS of all campaigns | |
| `qualified` | bool: `G >= MIN_G` | True |
| `rank_qual` | int or blank: rank among qualified campaigns only | 123 |
| `streak_len`, `in_long_streak` | int, bool | 4, True |
| `is_cle` | bool | True |
| `park` | str: home ballpark that season | Progressive Field |
| `lat`, `lon` | float: home ballpark that season | 41.4962, -81.6852 |
| `source` | str: where the counting stats came from (`lahman` or `mlb_api`) | lahman |

(Example numbers are placeholders, not real stats.)

## Deliverables and acceptance criteria

| Deliverable | Done when |
|---|---|
| `campaigns.csv` | `validate.py` passes: right row count per year, no duplicates, `PA > 0`, `0.3 < OPS < 1.2` for qualified campaigns, one `WS-W` per year and a result on every row, at least 25 AB per game for every team-series in `BattingPost.csv` (except campaigns overridden from the MLB Stats API), at least 7 of the 10 campaigns in `data/ref/spot_checks.csv` checked against an outside source (`check_ops`, `check_source`) and every checked one within ±.002, no null coordinates |
| View 1: Chart Party cut | 1920×1080 PNG hero still plus an MP4 flyover of 20–40 s. Cleveland is readable at a glance |
| View 2: 360 page | One HTML file. Opens offline (Plotly bundled). Drag to rotate 360°, scroll to zoom, hover shows team, year, OPS, PA and result. Has a Cleveland-only/streak-teams toggle |
| View 3: Skyline Earth | One HTML page plus a JSON file. Globe loads with no API key. Every campaign is a tower in its city. Click shows details. A fly-to dropdown lists every organization, and `?fly=CLE` opens on one directly. From far away each city shows one wide column |

## Out of scope (v1)

Park/era adjustment (OPS+), pitching, player-level drill-down, pre-1977 seasons.
