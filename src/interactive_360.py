"""View 2: the 360 page. Reads data/processed/campaigns.csv -> out/playoff_ops_360.html
Every campaign is a 3D tower (go.Mesh3d). X = year, Y = OPS rank within that year's field, Z = OPS.
Colour shows how far the team went. The page carries one record per campaign, and a small
script rebuilds the towers whenever a filter changes.
OPS is never recomputed here: every number comes straight from campaigns.csv."""
import json
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

BG, PANEL, GRID, TEXT, MUTED = "#0b0d10", "#10141a", "#1c2128", "#ffffff", "#9aa4b2"
# Colour = furthest round reached. One blue hue, darker to lighter as the run gets deeper
# (an ordinal ramp, validated for the dark surface with the dataviz palette checker).
LEVELS = [
    ("WC", "Lost in the Wild Card round", "#184f95"),
    ("DS", "Lost in the Division Series", "#256abf"),
    ("CS", "Lost in the League Championship Series", "#3987e5"),
    ("WS-L", "Lost the World Series", "#86b6ef"),
    ("WS-W", "Won the World Series", "#cde2fb"),
]
LEVEL_INDEX = {code: n for n, (code, _, _) in enumerate(LEVELS)}
FOOT = 0.56  # building footprint; the rest of each 1 x 1 cell is street
FLOOR = 0.03  # height of one storey (a dark spandrel band plus a lit window band), in drawn height units
SHAPES = 5    # building silhouettes; which one a campaign gets is arbitrary and carries no data
# Height contrast: differences from the median campaign are multiplied by this factor
# (1.0 would be true height from zero). One fixed setting, no control on the page.
MODES = [("Contrast", 2.0)]
DEFAULT_MODE = 0
MIN_HEIGHT = 0.02  # a tower never shrinks below this stub (the few weakest, very short campaigns)
DIM = 0.04  # opacity of towers that are filtered out but still shown as ghosts
OUT_FILE = C.OUT / "playoff_ops_360.html"


def fmt(x):
    return f"{x:.3f}".lstrip("0")


def hover(r, n_all, n_qual):
    rank = f"#{r.rank_all} of {n_all} campaigns"
    if r.qualified:
        rank += f"<br>#{int(r.rank_qual)} of {n_qual} with {C.MIN_G}+ games"
    else:
        rank += f"<br>Under {C.MIN_G} games, not ranked among full runs"
    streak = f"<br>Postseason streak: {r.streak_len} straight" if r.streak_len >= C.LONG_STREAK else ""
    return (f"<b>{r.year} {r.team_name}</b><br>{LEVELS[LEVEL_INDEX[r.result]][1]}<br>"
            f"<b>OPS {fmt(r.OPS)}</b>  (OBP {fmt(r.OBP)} / SLG {fmt(r.SLG)})<br>"
            f"{r.G} games, {r.PA} PA, {r.R_per_G:.1f} runs per game<br>"
            f"October average that year: {fmt(r.ps_avg_OPS)}<br>{rank}{streak}")


def mix(a, b, t):
    """Blend hex colour a toward hex colour b by fraction t."""
    pa, pb = (int(a[n:n + 2], 16) for n in (1, 3, 5)), (int(b[n:n + 2], 16) for n in (1, 3, 5))
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(pa, pb))


def empty_mesh(color, ghost):
    # A lit building is striped storey by storey: a darker facade band (cell value 0) and a
    # brighter window band (cell value 1), both tints of the result colour from the key.
    skin = dict(color=color) if ghost else dict(
        intensity=[], intensitymode="cell", cmin=0, cmax=1, showscale=False,
        colorscale=[[0, mix(color, BG, 0.42)], [1, mix(color, "#ffffff", 0.22)]])
    return go.Mesh3d(
        x=[], y=[], z=[], i=[], j=[], k=[], opacity=DIM if ghost else 1.0,
        flatshading=True, showlegend=False, **skin,
        # Plotly's own 3D hover label jumps between a tower's corners, so it is switched off.
        # "none" still fires hover events, which drive the page's own card. Ghosts are not hoverable.
        hoverinfo="skip" if ghost else "none",
        # Mostly ambient light, so a tower's faces stay close to its legend colour
        lighting=dict(ambient=0.82, diffuse=0.45, specular=0.03, roughness=0.95, fresnel=0.02),
        lightposition=dict(x=1900, y=-400, z=900),
    )


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Playoff OPS 360</title>
<style>
html,body{margin:0;height:100%;background:__BG__;color:#fff;font:13px/1.45 'Helvetica Neue',Arial,sans-serif}
body{display:flex;overflow:hidden}
#panel{flex:0 0 296px;box-sizing:border-box;padding:18px 16px 14px;background:__PANEL__;border-right:1px solid #1c2128;
  overflow-y:auto;display:flex;flex-direction:column;gap:13px}
#stage{flex:1;min-width:0;height:100vh}
h1{font-size:19px;line-height:1.2;margin:0}
p{margin:0;color:__MUTED__}
.lab,.ctl>label{display:block;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:__MUTED__;margin-bottom:5px}
#key{list-style:none;margin:0;padding:0}
#key li{display:flex;align-items:center;gap:8px;padding:2px 0;color:#dfe5ec}
#key i{flex:0 0 14px;height:14px;border-radius:2px}
#key b{margin-left:auto;font:12px Menlo,Consolas,monospace;font-weight:400;color:__MUTED__}
.grp{display:flex;gap:5px;flex-wrap:wrap}
button,select{font:12px 'Helvetica Neue',Arial,sans-serif;color:#c9d1d9;background:#151a21;border:1px solid #2a313b;
  border-radius:4px;padding:6px 10px;cursor:pointer}
select{width:100%}
button:hover,select:hover{border-color:#5b6470}
button.on{background:#e9edf2;color:__BG__;border-color:#e9edf2;font-weight:600}
input[type=range]{width:100%;accent-color:#e9edf2;margin:2px 0 0}
#gval{color:#fff;font-weight:600}
#count{color:#fff;font:12px Menlo,Consolas,monospace}
#reset{margin-top:6px}
#stage{position:relative;background:linear-gradient(to bottom,#04060a 0%,#0a0f1a 45%,#131d31 100%)}
#card{position:fixed;left:0;top:0;z-index:20;display:none;pointer-events:none;max-width:300px;box-sizing:border-box;
  padding:10px 12px;background:#151a21;border:1px solid #3a4350;border-left:4px solid #3987e5;border-radius:4px;
  font:12px/1.5 Menlo,Consolas,monospace;color:#fff;box-shadow:0 6px 24px rgba(0,0,0,.55);will-change:transform}
.notes{font-size:11px;margin-top:auto;padding-top:8px}
@media (max-width:760px){body{flex-direction:column;overflow:auto}#panel{flex:none;border-right:0;border-bottom:1px solid #1c2128}
  #stage{flex:none;height:78vh}}
</style></head><body>
<aside id="panel">
  <h1>Every postseason offense, __START__–__END__</h1>
  <p>__N__ campaigns. Each skyscraper is one team's whole postseason, and its height is that team's OPS. The best offense of each year stands in front.</p>
  <div><span class="lab">Colour key: how far the team went</span><ul id="key">__KEY__</ul></div>
  <div class="ctl"><label for="org">Organization</label><select id="org"><option value="">All organizations</option>__ORG_OPTIONS__</select></div>
  <div class="ctl"><label for="season">Season</label><select id="season"><option value="">All seasons</option>__SEASON_OPTIONS__</select></div>
  <div class="ctl"><label for="ming">Minimum games: <span id="gval">1</span></label>
    <input type="range" id="ming" min="1" max="__MAX_G__" step="1" value="1"></div>
  <div class="ctl"><span class="lab">Postseason streak</span><div class="grp" data-key="streak">
    <button data-v="any">Any</button><button data-v="long">__STREAK__+ straight years</button></div></div>
  <div class="ctl"><span class="lab">Filtered-out buildings</span><div class="grp" data-key="others">
    <button data-v="fade">Faded</button><button data-v="hide">Hidden</button></div></div>
  <div><div id="count"></div><button id="reset">Reset filters</button></div>
  <p class="notes">Drag to rotate, scroll to zoom, hover a building for details. No postseason was played in 1994.
  Height differences are drawn at twice their true size, measured from the median campaign, so good and bad Octobers stand apart. The axis and hover cards show true OPS. A building's top is its height; its shape (slab, setbacks, crown or spire) is decoration and means nothing.<br><br>
  Data: Lahman Baseball Database (CC BY-SA 3.0) and the MLB Stats API.</p>
</aside>
<main id="stage">__PLOT__</main>
<div id="card" role="status"></div>
<script>
var D=__DATA__, AXES=__AXES__, FOOT=__FOOT__, DEFAULT_MODE=__DEFAULT_MODE__, NG=__NG__;
var FLOOR=__FLOOR__,gd=document.getElementById('chart'),state,COLORS=__COLORS__,OWN=[];
function defaults(){return {org:'',season:'',minG:1,streak:'any',mode:DEFAULT_MODE,others:'fade'};}
// Geometry helpers. A quad is two triangles; v is its cell value (0 facade, 1 window).
function quad(t,ax,ay,az,bx,by,bz,cx,cy,cz,dx,dy,dz,v){
  var o=t.x.length;t.x.push(ax,bx,cx,dx);t.y.push(ay,by,cy,dy);t.z.push(az,bz,cz,dz);
  t.i.push(o,o);t.j.push(o+1,o+2);t.k.push(o+2,o+3);if(t.intensity)t.intensity.push(v,v);
}
function walls(t,cx,cy,hw,z0,z1,v){
  var x0=cx-hw,x1=cx+hw,y0=cy-hw,y1=cy+hw;
  quad(t,x0,y0,z0,x1,y0,z0,x1,y0,z1,x0,y0,z1,v);quad(t,x1,y0,z0,x1,y1,z0,x1,y1,z1,x1,y0,z1,v);
  quad(t,x1,y1,z0,x0,y1,z0,x0,y1,z1,x1,y1,z1,v);quad(t,x0,y1,z0,x0,y0,z0,x0,y0,z1,x0,y1,z1,v);
}
function roof(t,cx,cy,hw,z){quad(t,cx-hw,cy-hw,z,cx+hw,cy-hw,z,cx+hw,cy+hw,z,cx-hw,cy+hw,z,0);}
// One block of a building: storeys of facade band + window band, then a flat roof
function tier(t,cx,cy,hw,z0,z1){
  var z=z0,a,b;
  while(z<z1-1e-6){a=Math.min(z+FLOOR*0.42,z1);walls(t,cx,cy,hw,z,a,0);b=Math.min(z+FLOOR,z1);if(b>a)walls(t,cx,cy,hw,a,b,1);z=b;}
  roof(t,cx,cy,hw,z1);
}
function spire(t,cx,cy,hw,z0,z1){
  var o=t.x.length,q;t.x.push(cx-hw,cx+hw,cx+hw,cx-hw,cx);t.y.push(cy-hw,cy-hw,cy+hw,cy+hw,cy);t.z.push(z0,z0,z0,z0,z1);
  for(q=0;q<4;q++){t.i.push(o+q);t.j.push(o+(q+1)%4);t.k.push(o+4);t.intensity.push(0);}
}
// A lit skyscraper. Whatever the silhouette, its highest point is the campaign's height h.
function building(t,d,h){
  var cx=d.y,cy=d.s,hw=FOOT/2;
  if(h<FLOOR*5||d.k===0){tier(t,cx,cy,hw,0,h);}
  else if(d.k===1){tier(t,cx,cy,hw,0,h*0.62);tier(t,cx,cy,hw*0.76,h*0.62,h*0.86);tier(t,cx,cy,hw*0.5,h*0.86,h);}
  else if(d.k===2){tier(t,cx,cy,hw,0,h*0.9);tier(t,cx,cy,hw*0.45,h*0.9,h);}
  else if(d.k===3){tier(t,cx,cy,hw,0,h*0.88);spire(t,cx,cy,hw,h*0.88,h);}
  else{tier(t,cx,cy,hw,0,h*0.76);tier(t,cx,cy,hw*0.7,h*0.76,h);}
}
function draw(){
  var tr=[],n,shown=0;OWN=[];
  for(n=0;n<NG;n++)OWN.push([]);
  for(n=0;n<2*NG;n++)tr.push(n<NG?{x:[],y:[],z:[],i:[],j:[],k:[],intensity:[]}:{x:[],y:[],z:[],i:[],j:[],k:[]});
  D.forEach(function(d,ix){
    var pass=(!state.org||d.f===state.org)&&(!state.season||d.y===+state.season)&&d.G>=state.minG&&(state.streak==='any'||d.L);
    var h=d.h[state.mode];
    if(pass){shown++;building(tr[d.g],d,h);while(OWN[d.g].length<tr[d.g].i.length)OWN[d.g].push(ix);}
    else if(state.others!=='hide'){walls(tr[d.g+NG],d.y,d.s,FOOT/2,0,h,0);roof(tr[d.g+NG],d.y,d.s,FOOT/2,h);}
  });
  var data=gd.data.map(function(base,m){
    if(m>=2*NG)return base; // the ground slab
    var c={},key;for(key in base)c[key]=base[key];for(key in tr[m])c[key]=tr[m][key];
    c.visible=tr[m].x.length>0;return c;});
  var ax=AXES[state.mode],z=gd.layout.scene.zaxis;z.range=ax.range;z.tickvals=ax.tickvals;z.ticktext=ax.ticktext;
  Plotly.react(gd,data,gd.layout);
  document.getElementById('count').textContent='Showing '+shown+' of '+D.length+' campaigns';
}
function sync(){
  document.querySelectorAll('.grp').forEach(function(g){g.querySelectorAll('button').forEach(function(b){
    b.classList.toggle('on',String(state[g.dataset.key])===b.dataset.v);});});
  document.getElementById('org').value=state.org;document.getElementById('season').value=state.season;
  document.getElementById('ming').value=state.minG;document.getElementById('gval').textContent=state.minG;
}
function set(k,v){state[k]=v;sync();draw();}
document.querySelectorAll('.grp button').forEach(function(b){b.addEventListener('click',function(){
  var k=b.parentNode.dataset.key;set(k,k==='mode'?+b.dataset.v:b.dataset.v);});});
document.getElementById('org').addEventListener('change',function(e){set('org',e.target.value);});
document.getElementById('season').addEventListener('change',function(e){set('season',e.target.value);});
document.getElementById('ming').addEventListener('input',function(e){set('minG',+e.target.value);});
document.getElementById('reset').addEventListener('click',function(){state=defaults();sync();draw();});
state=defaults();sync();draw();
// Hover card: one card that follows the cursor. It changes only when the cursor moves to a
// different tower, and waits a moment before hiding, so it does not flicker between corners.
var card=document.getElementById('card'),cur=-1,hideTimer=null,mx=0,my=0;
function place(){
  var w=card.offsetWidth,h=card.offsetHeight,x=mx+18,y=my+18;
  if(x+w>window.innerWidth-8)x=mx-w-18;if(y+h>window.innerHeight-8)y=my-h-18;
  card.style.transform='translate('+Math.max(8,x)+'px,'+Math.max(8,y)+'px)';
}
window.addEventListener('mousemove',function(e){mx=e.clientX;my=e.clientY;if(cur>=0)place();},true);
gd.on('plotly_hover',function(e){
  var p=e.points&&e.points[0];if(!p)return;
  // For these meshes Plotly reports the hovered triangle; OWN maps each triangle of a lit
  // trace to its campaign. Ghosts and the ground are not hoverable.
  var own=OWN[p.curveNumber],ix=own?own[p.pointNumber]:undefined;
  if(ix===undefined)return;
  clearTimeout(hideTimer);
  if(ix!==cur){cur=ix;card.innerHTML=D[ix].t;card.style.borderLeftColor=COLORS[D[ix].g];card.style.display='block';}
  place();
});
function hide(){cur=-1;card.style.display='none';}
gd.on('plotly_unhover',function(){clearTimeout(hideTimer);hideTimer=setTimeout(hide,160);});
document.getElementById('stage').addEventListener('mouseleave',hide);
</script></body></html>
"""


def main():
    df = pd.read_csv(C.CAMPAIGNS_CSV)
    n_all, n_qual = len(df), int(df["qualified"].sum())
    # Y slot: 1 = best OPS in that year's field (front), worst at the back
    df["slot"] = df.groupby("year")["OPS"].rank(ascending=False, method="first").astype(int)

    # Drawn height: differences from the median campaign are multiplied by the mode's factor.
    # The transform is linear, so the z axis is still labelled in true OPS.
    median = df["OPS"].median()

    def to_height(ops, k):
        return median + k * (ops - median)

    def zaxis_for(k):
        ticks = [v for v in (0.3, 0.5, 0.7, 0.9) if to_height(v, k) > 0.03]
        return dict(range=[0, round(to_height(0.95, k), 4)], tickvals=[round(to_height(v, k), 4) for v in ticks],
                    ticktext=[fmt(v) for v in ticks])

    records = []
    for r in df.itertuples():
        heights = [round(max(MIN_HEIGHT, to_height(r.OPS, k)), 4) for _, k in MODES]
        records.append(dict(y=int(r.year), s=int(r.slot), g=LEVEL_INDEX[r.result], G=int(r.G), f=r.franch_id,
                            L=int(bool(r.in_long_streak)), h=heights, t=hover(r, n_all, n_qual),
                            k=(int(r.year) * 7 + sum(map(ord, r.franch_id))) % SHAPES))

    # Organizations: one entry per franchise, named as it was in its most recent campaign
    latest = df.sort_values("year").groupby("franch_id").tail(1).set_index("franch_id")["team_name"]
    counts = df.groupby("franch_id").size()
    orgs = sorted(((latest[f], f, int(counts[f])) for f in latest.index))
    org_options = "".join(f'<option value="{f}">{name} ({n})</option>' for name, f, n in orgs)
    season_options = "".join(f'<option value="{y}">{y} ({n} teams)</option>'
                             for y, n in sorted(df.groupby("year").size().items(), reverse=True))
    mode_buttons = "".join(f'<button data-v="{n}">{lab}</button>' for n, (lab, _) in enumerate(MODES))
    by_result = df.groupby("result").size()
    key = "".join(f'<li><i style="background:{color}"></i>{label}<b>{int(by_result.get(code, 0))}</b></li>'
                  for code, label, color in reversed(LEVELS))

    axis = dict(showbackground=False, gridcolor=GRID, zerolinecolor=GRID, color=MUTED,
                tickfont=dict(size=10, family="Menlo, Consolas, monospace"), showspikes=False)
    fig = go.Figure([empty_mesh(color, ghost) for ghost in (False, True) for _, _, color in LEVELS])
    # The ground the city stands on: one dark slab under the whole field
    gx0, gx1, gy0, gy1, gz = C.START_YEAR - 0.8, C.END_YEAR + 0.8, 0.2, 16.8, -0.012
    fig.add_trace(go.Mesh3d(
        x=[gx0, gx1, gx1, gx0, gx0, gx1, gx1, gx0], y=[gy0, gy0, gy1, gy1, gy0, gy0, gy1, gy1],
        z=[gz, gz, gz, gz, 0, 0, 0, 0], i=[0, 0, 4, 4, 0, 0, 1, 1, 2, 2, 3, 3], j=[1, 2, 5, 6, 1, 5, 2, 6, 3, 7, 0, 4],
        k=[2, 3, 6, 7, 5, 4, 6, 5, 7, 6, 4, 7], color="#161c26", flatshading=True, hoverinfo="skip", showlegend=False,
        lighting=dict(ambient=0.9, diffuse=0.2, specular=0, roughness=1, fresnel=0)))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT, family="Helvetica Neue, Arial, sans-serif"),
        margin=dict(l=0, r=0, t=0, b=0), hovermode="closest", uirevision="keep",
        scene=dict(
            bgcolor="rgba(0,0,0,0)", dragmode="turntable", uirevision="keep",
            xaxis=dict(axis, title=dict(text=""), tickmode="array",
                       tickvals=[1977, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2026],
                       range=[C.START_YEAR - 1, C.END_YEAR + 1]),
            yaxis=dict(axis, title=dict(text="OPS rank that year", font=dict(size=11)),
                       tickvals=[1, 4, 8, 12, 16], range=[0, 17]),
            zaxis=dict(axis, title=dict(text="OPS", font=dict(size=11)), tickmode="array",
                       **zaxis_for(MODES[DEFAULT_MODE][1])),
            # x and y cells are square on screen (52 by 17), so every tower has a square footprint
            aspectmode="manual", aspectratio=dict(x=3.0, y=0.98, z=0.42),
            camera=dict(eye=dict(x=-0.32, y=-2.95, z=1.0), center=dict(x=0.06, y=0, z=-0.2), up=dict(x=0, y=0, z=1)),
        ),
    )
    plot = pio.to_html(fig, full_html=False, include_plotlyjs=True, div_id="chart",
                       config={"displaylogo": False, "responsive": True, "scrollZoom": True},
                       default_width="100%", default_height="100%")

    fill = {
        "__BG__": BG, "__PANEL__": PANEL, "__MUTED__": MUTED, "__START__": str(C.START_YEAR), "__END__": str(C.END_YEAR),
        "__N__": str(n_all), "__STREAK__": str(C.LONG_STREAK), "__KEY__": key, "__ORG_OPTIONS__": org_options,
        "__SEASON_OPTIONS__": season_options, "__MAX_G__": str(int(df["G"].max())), "__MODE_BUTTONS__": mode_buttons,
        "__DATA__": json.dumps(records, separators=(",", ":")).replace("</", "<\\/"),
        "__AXES__": json.dumps([zaxis_for(k) for _, k in MODES]), "__FOOT__": str(FOOT), "__FLOOR__": str(FLOOR),
        "__DEFAULT_MODE__": str(DEFAULT_MODE), "__NG__": str(len(LEVELS)), "__PLOT__": plot,
        "__COLORS__": json.dumps([color for _, _, color in LEVELS]),
    }
    html = PAGE
    for token, value in fill.items():
        html = html.replace(token, value)

    C.OUT.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(C.ROOT)} ({OUT_FILE.stat().st_size / 1e6:.1f} MB): {n_all} towers, "
          f"{len(orgs)} organizations, {df['year'].nunique()} seasons, games 1-{int(df['G'].max())}")


if __name__ == "__main__":
    main()
