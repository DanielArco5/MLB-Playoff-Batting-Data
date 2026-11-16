# 04 — View 2: The 360 Page

Every postseason campaign as a skyscraper in one city-like field. Drag to spin it, scroll to zoom, hover any building, and filter by organization, season, games played or streak. This is the skyscraper view; Skyline Earth (view 3) is the separate globe.

**Output:** `out/playoff_ops_360.html` (one self-contained file, about 5 MB, opens offline).
**Script:** `src/interactive_360.py` with Plotly. It reads `data/processed/campaigns.csv` and never recomputes OPS.

## Layout: the October field

| Axis | Meaning |
|---|---|
| X | Year, 1977 to 2026. 1994 is an empty gap, left visible on purpose |
| Y | That year's playoff teams, sorted by OPS: best in front, worst at the back |
| Z | Campaign OPS, drawn with doubled contrast (see below) |

Each building has a 0.56 × 0.56 footprint inside a 1 × 1 cell, so the rest of every cell is open "street". The scene's aspect ratio keeps the cells square, so every footprint is square. The field stands on one dark ground slab, under a night-sky gradient.

## Skyscraper look

- **Storeys:** every building is striped floor by floor. One storey is 0.03 height units: a darker facade band and a brighter window band. Both are tints of the building's key colour, so the colour key still reads.
- **Silhouettes:** five shapes (plain slab, three-step setback, slab with a narrow crown, slab with a pyramid spire, two-step setback). Which shape a campaign gets comes from a fixed hash of its year and franchise. **The shape carries no data.**
- **The top is the data.** Whatever the shape, a building's highest point is the campaign's height. Upper tiers start no lower than 62% of the way up, and the main body always reaches at least 62% (most reach 76–90%).
- Buildings shorter than five storeys are plain slabs.
- Filtered-out ghosts are plain translucent boxes with no storeys.

## Height: doubled contrast

Most campaigns fall between .600 and .800, so true heights from zero look like a flat wall. Heights are therefore stretched around the median campaign:

```
height = median_OPS + 2.0 × (OPS − median_OPS)
```

- The factor is `MODES = [("Contrast", 2.0)]` in the script. There is one fixed setting and no control on the page.
- The transform is linear, so the Z axis is still labelled in **true OPS** (.300, .500, .700, .900), and the hover card shows true OPS.
- A tower never shrinks below a 0.02 stub. That only affects the five weakest campaigns, all very short series.
- The page says this in its notes. Do not present the heights as true to scale.

## Colour: how far the team went

Colour is the furthest round reached, as one blue hue that gets lighter as the run gets deeper. The ramp was checked with the dataviz palette validator for the dark background (ordinal mode).

| Result | Colour |
|---|---|
| Lost in the Wild Card round | `#184f95` |
| Lost in the Division Series | `#256abf` |
| Lost in the League Championship Series | `#3987e5` |
| Lost the World Series | `#86b6ef` |
| Won the World Series | `#cde2fb` |

The left panel carries the colour key with a count for each level. No team has its own colour. Cleveland is one of the 30 organizations in the filter.

## Controls (left panel)

| Control | Behaviour |
|---|---|
| Organization | Dropdown of all 30 franchises, each under its most recent name, with its number of campaigns |
| Season | Dropdown of every season, newest first |
| Minimum games | Slider from 1 to 20 |
| Postseason streak | Any, or only campaigns inside a run of 4+ straight postseasons |
| Filtered-out towers | **Faded** (ghosts at 4% opacity, the default) or **Hidden** |
| Counter and reset | "Showing N of 374 campaigns" and a Reset filters button |

The filters combine. Towers keep their place when filtered: a tower's Y slot is its OPS rank in the full field for that year.

## How it is built

- Plotly has no 3D bar, so every building is triangles in a `go.Mesh3d`. A lit building is a few hundred triangles (four walls per band, plus roofs); the whole field is about 130,000.
- There are eleven traces: one per colour level for lit buildings, one per colour level for ghosts, and the ground slab.
- Lit traces use `intensitymode="cell"` with a two-stop colorscale (facade tint, window tint), so each triangle is one or the other.
- The page embeds one small record per campaign. A script on the page rebuilds the meshes whenever a control changes (about 90 ms) and calls `Plotly.react`. `uirevision` keeps the camera where the reader left it.
- `scene.dragmode` is `turntable`, so the field spins without tumbling.

## Hover card

Plotly's own 3D hover label snaps to a building's nearest corner and jumps around, so it is switched off (`hoverinfo="none"`, which still fires hover events). For these meshes the event's `pointNumber` is the hovered triangle, and the page keeps a triangle-to-campaign table for each lit trace. The page shows its own card instead:

- It follows the cursor and flips to the other side near the window edge.
- Its content changes only when the cursor reaches a different tower.
- It waits 160 ms before hiding, so it does not flicker in the gaps.
- Ghost towers are not hoverable.

The card shows team and year, result, OPS with OBP/SLG, games, PA, runs per game, that October's average OPS, rank of all 374, rank among campaigns with 8+ games, and the streak length when it is 4 or more.

## Look

Background `#0b0d10`, panel `#10141a`, gridlines `#1c2128`, white and gray text, mostly ambient lighting so tower faces stay close to their key colour. The panel stacks above the chart on narrow screens.

## Not built

- A switch between raw OPS and OPS versus that October's average.
- Auto-spin on load.
- A Three.js port.
