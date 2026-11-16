# 03 — View 1: "Chart Party" 3D Bar Field

A documentary-style 3D bar chart in the spirit of Jon Bois's Secret Base videos: an empty dark plane, bars rising out of it, and a slow camera that does the storytelling. This is an original take on that mood. It doesn't copy their graphics, fonts or branding.

**Output:** `out/chart_party/hero.png` (1920×1080) and `out/chart_party.mp4` (20–40 s).
**Script:** `src/chart_party.py`, built with matplotlib `Axes3D.bar3d`.

## Layout: the "October field"

| Axis | Meaning |
|---|---|
| X (left to right) | Year, 1977 to 2026. 1994 is an empty gap, left visible on purpose |
| Y (depth) | That year's playoff teams, **sorted by OPS** (best in front, worst at the back) |
| Z (height) | Campaign OPS, **starting from 0** so heights are honest |

Result: a skyline that gets wider and deeper as the playoffs expand. The format history comes along for free.

## Style guide

| Element | Spec |
|---|---|
| Background | Near-black `#0b0d10`; hide the panes; faint floor grid `#1c2128` |
| Bars (all teams) | Flat muted gray `#5b6470`, slight transparency (alpha 0.85), `shade=True` |
| Cleveland bars | One highlight color, e.g. `#e8553e`, full opacity |
| 4+ streak teams (optional pass) | Pale steel `#9fb3c8` |
| Text | White/off-white, one sans or mono font, few labels: year ticks every 5 years and an OPS reference line at the postseason average |
| Annotations | Big plain-language captions burned into frames ("This is every playoff offense since 1977."), one idea per shot |

## Camera script (the video)

Render frames by changing `ax.view_init(elev, azim)` and `ax.dist` (or the axis limits for zoom), then stitch with ffmpeg.

| Shot | Seconds | Camera | Caption idea |
|---|---|---|---|
| 1 | 0–6 | Low and close on one dim gray bar, slowly rising | "This is one team's October." |
| 2 | 6–14 | Pull back and up to reveal the whole field | "This is all ~374 of them." |
| 3 | 14–22 | Light up Cleveland's bars, everything else dims to alpha 0.25 | "These are Cleveland's." |
| 4 | 22–32 | Slow orbit (azim +90°) at a mid elevation | Rank call-out: "Cleveland's best: #__. Worst: #__ of 374." |
| 5 | 32–40 | Switch the highlight to the 4+ streak teams, Cleveland stays lit | "Other teams that kept getting chances." |

```python
# sketch: frame loop
for i, t in enumerate(np.linspace(0, 1, n_frames)):
    elev, azim, zoom = camera_path(t)          # interpolate between shot keyframes
    ax.view_init(elev=elev, azim=azim)
    fig.savefig(f"out/chart_party/frames/{i:04d}.png", dpi=100, facecolor=BG)
# ffmpeg -framerate 30 -i out/chart_party/frames/%04d.png -c:v libx264 -preset veryfast -pix_fmt yuv420p out/chart_party.mp4
```

Ease the camera with smoothstep `t*t*(3-2*t)` between keyframes. Linear moves look robotic.

## Gotchas

- matplotlib 3D has no real depth sorting, so bars can draw in the wrong order at some angles. Draw back rows first (sort by Y descending) and avoid extreme low angles.
- About 374 `bar3d` calls are fine. Do **one call per color group** (pass arrays) for speed.
- Set `ax.set_box_aspect((years, max_teams, height_scale))` so the field reads wide, not cubic.
