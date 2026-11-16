# 05 — View 3: Skyline Earth

Every postseason campaign is a skyscraper standing in its team's city on a 3D globe. Higher OPS means a taller tower. Each organization's campaigns form a small downtown around its ballpark.

**Output:** `src/skyline_earth/index.html` + `campaigns.json`.
**Scripts:** `src/export_globe_json.py` writes the JSON from `data/processed/campaigns.csv`. The page is hand-written.
**Tech:** CesiumJS 1.123 from cesium.com, with OpenStreetMap tiles. No API key or account is needed. The page needs an internet connection for both.

## Height scale: true to scale

Unlike the 360 page, heights here are not stretched. Height = `OPS × 1000 m × slider`.

- At ×1, a .828 OPS tower is 828 m, the height of the Burj Khalifa.
- The slider runs from ×1 to ×50 and scales every tower and every city column the same way. The panel states the current scale.

## Colour

The same key as the 360 page: one blue hue from `#184f95` (lost in the Wild Card round) to `#cde2fb` (won the World Series). The map is dimmed (brightness 0.42, saturation 0.15) so the towers carry the colour. The scene light points along the camera, so towers never fall into night shadow.

## Placement: downtown grids

`export_globe_json.py` computes every position, so the page stays simple.

- Towers are 150 m wide and stand 250 m apart, centre to centre.
- A downtown is a square spiral ordered by year: the oldest campaign is at the centre.
- One downtown per organization per city. An organization's ballparks within 40 km of each other share a downtown, centred on the most recent one (so Atlanta's three parks make one downtown at Truist Park).
- **Second downtowns:** a team stands where it played that year. The 1981 Expos have their own one-tower downtown in Montreal, apart from the Nationals in Washington. The 2020 Blue Jays stand in Buffalo (Sahlen Field), apart from Toronto. That makes 32 downtowns for 30 organizations.

## Far zoom: one column per city

Towers are 150 m wide, so they vanish at national zoom. Each downtown also has one wide column:

- **Width:** 40 km square.
- **Height:** the median OPS of the campaigns standing in that city, on the same true scale as the towers and with the same slider. At ×1 it is a low slab that reads as a coloured square from above. Raise the slider to see height from far away.
- **Colour:** the median finish of those campaigns on the same key (the lower-middle one when the count is even).
- **Fade:** solid when the camera is 300 km or more from the city, gone inside 90 km, and smoothly translucent in between. A hidden column cannot be clicked.
- **Shared metros:** New York, Chicago and the Bay Area each hold two organizations closer together than a column is wide. Their columns are pushed apart to 44 km between centres, so each one sits 14 to 17 km from its ballpark. The towers stay at the real ballparks.
- Columns summarise every campaign in the city and ignore the filters.
- Clicking a column or a city label flies to that downtown.

## Controls (left panel)

| Control | Behaviour |
|---|---|
| Fly to a skyline | Dropdown of every downtown, sorted by number of towers. Flies to a low oblique view |
| Whole map | Returns to the national view |
| Click a tower | Details appear in the panel and the tower gets a white outline |
| Tower height | Slider, ×1 to ×50 |
| Season | Every season, newest first |
| Minimum games | Slider from 1 to 20 |
| Postseason streak | Any, or only campaigns in a run of 4+ straight postseasons |
| Counter and reset | "Showing N of 374 campaigns" and a Reset filters button |

**Ghosting:** towers that fail a filter stay in place at 10% opacity with no outline.

There is no "Fly to Cleveland" button. Cleveland is in the dropdown, and the deep link below opens straight onto it.

## Deep links

`index.html?fly=CLE&mult=3` opens on that organization's skyline at that height. `fly` takes a Lahman franchise ID (`CLE`, `NYY`, `LAD`, ...) and `mult` a number from 1 to 50.

## `campaigns.json`

```json
{ "meta":   { "campaigns": 374, "qualified": 161, "minG": 8, "footprint": 150, "spacing": 250, "columnWidth": 40000, ... },
  "places": [ { "franch": "CLE", "name": "Cleveland Guardians", "park": "Progressive Field", "lat": 0, "lon": 0,
                "count": 16, "radius": 750, "medOps": 0.000, "medResult": "DS", "colLat": 0, "colLon": 0 } ],
  "towers": [ { "year": 2016, "team": "Cleveland Indians", "franch": "CLE", "ops": 0.000, "obp": 0.000, "slg": 0.000,
                "pa": 0, "g": 0, "result": "WS-L", "rank": 0, "rankQual": 0, "lon": 0, "lat": 0,
                "streak": true, "streakLen": 0, "place": 0 } ] }
```
(Values are placeholders.) Every statistic is copied from `campaigns.csv`. The only numbers made here are grid positions and each city's medians.

## Running it

Browsers block `fetch()` from `file://`, so serve the folder:

```bash
python src/export_globe_json.py
cd src/skyline_earth && python3 -m http.server 8000
# then open http://localhost:8000
```
Opened straight from disk, the page shows these instructions instead of a blank globe.

## Credits on the page

"Map data © OpenStreetMap contributors" (required by OSM's tile usage policy) and "Stats: Lahman Baseball Database (CC BY-SA 3.0) and the MLB Stats API". Cesium's own credit strip stays visible. OSM's public tile servers are fine for personal projects. If the page ever gets real traffic, switch to a tile provider with a free key.
