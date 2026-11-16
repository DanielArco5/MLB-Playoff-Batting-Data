# CLAUDE.md — working rules for this repo

Read `docs/01_SPEC.md` before writing code. The definitions there (campaign, OPS math, streaks) are fixed. Don't improvise them.

- **One source of truth:** every chart reads `data/processed/campaigns.csv`. Never recompute OPS inside a chart script.
- **OPS is computed from summed counting stats** (H, 2B, 3B, HR, BB, HBP, AB, SF), never by averaging per-series or per-player OPS. See the formula in the spec.
- **Never edit files in `data/raw/`.** Fixes go in `build_campaigns.py` or in `data/ref/` lookup tables.
- **No scraping loops against Baseball-Reference.** Sports Reference blocks anything faster than 20 requests a minute, and its terms forbid building tools from scraped data. Use the Lahman CSVs, plus the saved MLB Stats API responses in `data/raw/mlb_api/` (one request per season) for 2026 and the overrides in `data/ref/mlb_api_overrides.csv`. Touch BR only for manual spot checks.
- `src/validate.py` must pass before any chart is built.
- Cleveland is identified by `franch_id == "CLE"` (Indians before 2022, Guardians from 2022). Never match on team name.
- Styling: dark background, plain sans/mono labels. No team logos or league marks.
- **Colour means how far the team went**, in both interactive views: one blue hue from `#184f95` (lost in the Wild Card round) through `#256abf`, `#3987e5`, `#86b6ef` to `#cde2fb` (won the World Series). Always show the colour key. One exception: in the City view of `out/playoff_ops_city.html` every building is modelled on a different real tower and wears that tower's colour (twelve detailed landmarks for the twelve best qualified campaigns; the rest are simplified likenesses listed in `src/real_towers.py`), and the result colour is the plate under each building (its Bars view keeps the ramp). The cars, people, trees and lamps there are decoration. No team gets its own colour; Cleveland is picked through the organization filter or `?fly=CLE`.
- Filters (organization, season, minimum games, 4+ year streak) fade non-matching towers to ghosts; they don't move or recolour the rest.
- **Heights:** the 360 page draws differences at twice their true size around the median campaign and says so on the page; its axis and hover card show true OPS. Skyline Earth is true to scale (`OPS × 1000 m × slider`). Don't mix the two.
- A campaign needs 8+ games (`MIN_G`) to be ranked among full runs (`qualified`, `rank_qual`).
- Keep each view's output to a single self-contained file (PNG/MP4/HTML) in `out/`. The exception is Skyline Earth, which is `src/skyline_earth/index.html` plus `campaigns.json` and has to be served over http.
