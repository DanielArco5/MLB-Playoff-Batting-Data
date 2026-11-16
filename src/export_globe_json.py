"""View 3 data: data/processed/campaigns.csv -> src/skyline_earth/campaigns.json
Places every campaign as a tower in a "downtown" grid around its team's ballpark.
All numbers come straight from campaigns.csv; nothing is recomputed here."""
import json
import math
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

OUT_FILE = C.ROOT / "src" / "skyline_earth" / "campaigns.json"
SPACING_M = 250.0       # centre-to-centre distance between towers
FOOTPRINT_M = 150.0     # tower width and depth
M_PER_DEG_LAT = 111_320.0
SAME_CITY_KM = 40.0     # a franchise's ballparks closer than this share one downtown
COLUMN_M = 40_000.0     # width of the one-per-city column shown from far away
COLUMN_GAP = 1.1        # neighbouring columns are pushed apart to this many widths, centre to centre
RESULT_ORDER = ["WC", "DS", "CS", "WS-L", "WS-W"]


def spiral(n):
    """Grid cells (east, north) spiralling out from (0, 0): the first cell is the centre."""
    cells, x, y, dx, dy = [], 0, 0, 1, 0
    step, used, turns = 1, 0, 0
    for _ in range(n):
        cells.append((x, y))
        x, y = x + dx, y + dy
        used += 1
        if used == step:
            used, turns = 0, turns + 1
            dx, dy = -dy, dx
            if turns % 2 == 0:
                step += 1
    return cells


def km_between(lat1, lon1, lat2, lon2):
    x = math.radians(lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    y = math.radians(lat2 - lat1)
    return 6371.0 * math.hypot(x, y)


def spread_columns(places):
    """Give each city column its own spot. Cities that share a metro area (New York, Chicago,
    the Bay Area) would overlap, so each close pair is pushed apart along the line between them."""
    for p in places:
        p["colLat"], p["colLon"] = p["lat"], p["lon"]
    need = COLUMN_M * COLUMN_GAP / 1000.0
    for _ in range(50):
        moved = False
        for a in places:
            for b in places:
                if a is b:
                    continue
                d = km_between(a["colLat"], a["colLon"], b["colLat"], b["colLon"])
                if d >= need - 0.01:
                    continue
                moved = True
                k = (need - d) / 2 / max(d, 0.001)  # each one moves half of the shortfall
                dlat, dlon = a["colLat"] - b["colLat"], a["colLon"] - b["colLon"]
                a["colLat"] += dlat * k; a["colLon"] += dlon * k
                b["colLat"] -= dlat * k; b["colLon"] -= dlon * k
        if not moved:
            break
    for p in places:
        p["colLat"], p["colLon"] = round(p["colLat"], 5), round(p["colLon"], 5)


def main():
    df = pd.read_csv(C.CAMPAIGNS_CSV).sort_values(["franch_id", "year"])
    n_all, n_qual = len(df), int(df["qualified"].sum())

    # Downtowns: one per franchise per city. The centre is the most recent ballpark there.
    downtowns = []  # dict(franch, lat, lon, park, rows)
    for franch, rows in df.groupby("franch_id"):
        local = []
        for r in rows.sort_values("year", ascending=False).itertuples():
            home = next((d for d in local if km_between(d["lat"], d["lon"], r.lat, r.lon) <= SAME_CITY_KM), None)
            if home is None:
                home = dict(franch=franch, lat=r.lat, lon=r.lon, park=r.park, name=r.team_name, rows=[])
                local.append(home)
            home["rows"].append(r)
        downtowns += local

    towers, places = [], []
    for d in downtowns:
        rows = sorted(d["rows"], key=lambda r: r.year)
        dlat = SPACING_M / M_PER_DEG_LAT
        dlon = dlat / math.cos(math.radians(d["lat"]))
        ring = 0
        for r, (gx, gy) in zip(rows, spiral(len(rows))):
            ring = max(ring, abs(gx), abs(gy))
            towers.append(dict(
                year=int(r.year), team=r.team_name, franch=r.franch_id, park=r.park,
                ops=float(r.OPS), obp=float(r.OBP), slg=float(r.SLG), pa=int(r.PA), g=int(r.G),
                rpg=float(r.R_per_G), psAvg=float(r.ps_avg_OPS), result=r.result,
                rank=int(r.rank_all), rankQual=None if pd.isna(r.rank_qual) else int(r.rank_qual),
                lon=round(d["lon"] + gx * dlon, 6), lat=round(d["lat"] + gy * dlat, 6),
                isCle=bool(r.is_cle), streak=bool(r.in_long_streak), streakLen=int(r.streak_len),
                place=len(places)))
        # Far-zoom column: the median campaign standing in this city. The OPS values are taken
        # as they are from campaigns.csv; the median finish is the lower-middle one when the count is even.
        ops_values = pd.Series([r.OPS for r in rows])
        finishes = sorted(RESULT_ORDER.index(r.result) for r in rows)
        places.append(dict(franch=d["franch"], name=d["name"], park=d["park"], lat=d["lat"], lon=d["lon"],
                           count=len(rows), first=int(rows[0].year), last=int(rows[-1].year),
                           radius=round((ring + 1) * SPACING_M), medOps=round(float(ops_values.median()), 3),
                           medResult=RESULT_ORDER[finishes[(len(finishes) - 1) // 2]]))
    spread_columns(places)

    payload = dict(
        meta=dict(startYear=C.START_YEAR, endYear=C.END_YEAR, campaigns=n_all, qualified=n_qual, minG=C.MIN_G,
                  longStreak=C.LONG_STREAK, footprint=FOOTPRINT_M, spacing=SPACING_M, columnWidth=COLUMN_M, maxG=int(df["G"].max())),
        places=places, towers=towers)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    multi = [p["name"] + f" ({p['park']}, {p['count']})" for p in places
             if sum(q["franch"] == p["franch"] for q in places) > 1]
    print(f"Wrote {OUT_FILE.relative_to(C.ROOT)}: {len(towers)} towers in {len(places)} downtowns")
    print("Franchises with more than one downtown:", "; ".join(multi) if multi else "none")
    shifted = [f"{p['name']} {km_between(p['lat'], p['lon'], p['colLat'], p['colLon']):.0f} km" for p in places
               if km_between(p["lat"], p["lon"], p["colLat"], p["colLon"]) > 0.5]
    print("City columns moved off their ballpark to avoid overlap:", "; ".join(shifted) if shifted else "none")


if __name__ == "__main__":
    main()
