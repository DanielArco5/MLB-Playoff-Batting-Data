# 06 — The city page

`src/skyline_city.py` → `out/playoff_ops_city.html`. One self-contained file (three.js r147 is bundled from `src/vendor/`), opens offline by double-click.

## What it shows

The same field as the 360 page: one position per campaign, seasons left to right, the best OPS of each season in front. Height is OPS with the same doubled contrast (differences from the median campaign drawn at twice their size); the ruler and hover cards show true OPS. Every number comes from `campaigns.csv`.

A **View** switch offers two versions of that field:

| | City | Bars |
|---|---|---|
| Mark | A modelled building | A plain square bar |
| Spacing | One city block per campaign (3.4 units) | Tight rows (1.8 units) |
| Result colour | The plate under the building and the edge of the hover card | The bar itself |
| Extras | Roads, traffic, people, parks, low-rises | None |

`?view=bars` opens in Bars. `?look=2007-BOS` opens close to one building. `?catalog` opens the catalog.

## Buildings

- **Every building is modelled on a different real tower**, named on its hover card ("Modelled on: Key Tower, Cleveland") and in the catalog. 374 campaigns, 374 towers.
- **Twelve detailed landmarks.** The twelve best full runs (8+ games) get hand-built models, tallest real tower first: Burj Khalifa, Shanghai Tower, One World Trade Center, Taipei 101, Petronas Towers, Willis Tower, Empire State Building, John Hancock Center, Chrysler Building, The Shard, Transamerica Pyramid, 30 St Mary Axe.
- **362 simplified likenesses.** The other towers are listed in `src/real_towers.py`, each with four traits the model follows: overall form, crown, facade type and colour. Finer proportions come from a random stream seeded by the campaign, so these are likenesses, not replicas. The list runs roughly from the tallest and best known down and is handed out in order of OPS.
- **Short buildings are scaled-down towers**, not squat blocks.
- **The highest point is the height**, spire included.
- **Catalog.** "Check every building" lists all 374, grouped by organization in season order. Each picture is zoomed to fit, so sizes there do not compare. Clicking one flies to it.

## What is decoration

The page says this in its notes; keep it true.

- Which real tower a campaign has, and which windows are lit.
- Roads, cars, traffic lights, people, trees, lamps, parks.
- The plain dark low-rise blocks. They have no plate and no hover card, and stand only where there is no campaign or in the corners of a campaign's block.

## The city layout

Scale: one storey is 0.09 units (about 3 m), so a block is about 110 m.

- Roads run on the boundaries between cells: two lanes each way, kerb, pavement, zebra crossings in line with the pavements, stop lines.
- Cars keep to their lane on the right, queue behind the car in front, and stop at red lights. Lights alternate between the two directions on a 14-second cycle.
- People walk the pavements. They ignore the lights.
- Motion stops when the browser asks for reduced motion.

## Filters

Organization, season, minimum games, 4+ year streak, and faded/hidden for the rest, as on the 360 page.

## Keeping it smooth

- Small parts of a building (roofs, trim, masts, beacon, plate) share two vertex-coloured materials, so a building is about three draw calls.
- Materials are Lambert, the canvas is opaque, and the pixel ratio is capped at 1.5.
- If frames run longer than about 24 ms for a while, the page lowers its render resolution step by step and updates the walkers less often.
