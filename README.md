# Playoff OPS Skyline

How good (or bad) has every postseason offense of the last 50 years been, and where does Cleveland sit among them?

The project turns every MLB team's postseason campaign from **1977–2026** into a 3D bar or building. Its height is that team's OPS over the whole postseason.

**Start here:** open `out/playoff_ops_city.html` in a browser (no server needed), and read [docs/FINDINGS.md](docs/FINDINGS.md) for what the data shows.

Views:

| # | View | What it is | Tech |
|---|------|------------|------|
| 1 | **Chart Party cut** (not built yet) | A documentary-style 3D bar field with a slow camera flyover, exported as video/stills | Python, matplotlib `bar3d`, ffmpeg |
| 2 | **The 360 page** | A single HTML page with every campaign as a 3D bar you can rotate, zoom and hover | Python, Plotly (`Mesh3d`), standalone HTML |
| 2b | **The city page** | Every campaign as its own skyscraper in a city with streets and traffic, or as plain bars; `out/playoff_ops_city.html` | Python, three.js, standalone HTML |
| 3 | **Skyline Earth** | Every campaign as a skyscraper on a 3D globe, standing in its team's city. Higher OPS means a taller tower | CesiumJS (free, no token), single HTML page |

## Folder layout

```
playoff-ops-skyline/
├── README.md                 ← you are here
├── CLAUDE.md                 ← instructions for Claude Code in VS Code
├── docs/
│   ├── 01_SPEC.md            ← scope, definitions, acceptance criteria
│   ├── 02_DATA_PIPELINE.md   ← where the data comes from and how it's cleaned
│   ├── 03_CHART_PARTY_3D.md  ← view 1 (video-style 3D bars)
│   ├── 04_INTERACTIVE_360.md ← view 2 (rotatable page)
│   ├── 05_SKYLINE_EARTH.md   ← view 3 (skyscrapers on a globe)
│   ├── 06_SKYLINE_CITY.md    ← the city page
│   └── FINDINGS.md           ← write-up: trends in 50 years of October offense
├── data/
│   ├── raw/                  ← untouched downloads/exports (never edited)
│   ├── ref/                  ← hand-made lookup tables (franchises, ballparks)
│   └── processed/
│       └── campaigns.csv     ← the one clean table every view reads
├── src/
│   ├── build_campaigns.py    ← raw → processed/campaigns.csv
│   ├── validate.py           ← sanity checks + hand spot checks
│   ├── fetch_mlb_api.py      ← saves MLB Stats API responses (one request per season)
│   ├── compare_sources.py    ← audits Lahman and campaigns.csv against the API
│   ├── skyline_city.py       ← the city page
│   ├── chart_party.py        ← view 1 (not built yet)
│   ├── interactive_360.py    ← view 2
│   └── skyline_earth/        ← view 3 (index.html + campaigns.json)
└── out/                      ← rendered PNGs, MP4s, HTML pages
```

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install pandas numpy plotly
# ffmpeg is needed only for the video (brew install ffmpeg / winget install ffmpeg)

# 1. Put the raw data in data/raw/ (see docs/02_DATA_PIPELINE.md)
python src/build_campaigns.py      # → data/processed/campaigns.csv
python src/validate.py             # must pass before building any chart

python src/compare_sources.py      # optional audit against the saved MLB Stats API responses

python src/interactive_360.py      # → out/playoff_ops_360.html
python src/skyline_city.py         # → out/playoff_ops_city.html
python src/export_globe_json.py    # → src/skyline_earth/campaigns.json
# then open src/skyline_earth/index.html with VS Code's Live Server extension
```

## Build order

1. Data first (`02_DATA_PIPELINE.md`). Every view reads `campaigns.csv`, so get it right once.
2. View 2 (360 page). This is the fastest way to spot bad data, because you can hover any bar.
3. View 1 (Chart Party cut).
4. View 3 (Skyline Earth).

## Data credit

Built from Lahman's Baseball Database (CC BY-SA 3.0), with 2026 and four incomplete campaigns (three from 2023, one from 2024) from the public MLB Stats API. Every campaign is cross-checked against the MLB Stats API, and seven were checked by hand against StatMuse. `data/processed/campaigns.csv` is derived from Lahman and is shared under the same CC BY-SA 3.0 terms. See `docs/02_DATA_PIPELINE.md` for the usage rules.

three.js (MIT) is bundled in `src/vendor/`.
