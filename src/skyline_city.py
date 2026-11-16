"""The city view and the plain bars view: every campaign as a skyscraper modelled on a real tower
(Burj Khalifa, Empire State Building, ...), or as a plain bar; a switch on the page picks which. Reads data/processed/campaigns.csv
-> out/playoff_ops_city.html (one self-contained file; three.js is bundled from src/vendor/).
Same field, heights, colours, filters and hover card as interactive_360.py, drawn with three.js
so buildings can have real facades, windows and rooflines.
OPS is never recomputed here: every number comes straight from campaigns.csv."""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
import real_towers
from interactive_360 import BG, LEVEL_INDEX, LEVELS, MIN_HEIGHT, MODES, MUTED, PANEL, fmt, hover

VENDOR = C.ROOT / "src" / "vendor"
OUT_FILE = C.OUT / "playoff_ops_city.html"
CONTRAST = MODES[0][1]  # same doubled contrast as the 360 page
HEIGHT_SCALE = 4.2      # scene units per 1.0 of drawn height (a cell is 1 x 1 scene unit)
FOOT = 0.56             # building footprint, scene units
PITCH = 1.8             # Bars view: distance between neighbouring bars (centre to centre), scene units
CITY_PITCH = 3.4        # City view: one city block per campaign; a storey is 0.09, so a block is about 110 m
ROAD_HALF = 0.21        # half the width of a road (two lanes each way)
SIDEWALK = 0.12         # pavement width
STOREY = 0.09           # scene units per storey
STYLES = 4              # facade styles (masonry, ribbon windows, glass, finned glass); set per building type on the page
LOW_RISE = 0.6          # buildings shorter than this (scene units) are drawn as a plain low-rise block
# Real towers modelled on the page. The order must match the switch in build() on the page.
# They go, one each, to the twelve best qualified campaigns (LANDMARK_ORDER: tallest real tower first);
# every other campaign gets a generated one-of-a-kind design.
BUILDINGS = ["Burj Khalifa", "Empire State Building", "Chrysler Building", "Willis Tower", "Taipei 101",
             "One World Trade Center", "Petronas Towers", "Transamerica Pyramid", "The Shard",
             "John Hancock Center", "Shanghai Tower", "30 St Mary Axe (the Gherkin)"]
LANDMARK_ORDER = [0, 10, 5, 4, 6, 3, 1, 9, 2, 8, 7, 11]
# Facade colours for the generated designs
PALETTE = ["#c9d3dd", "#d6cbb2", "#b9b4a8", "#8c9aa8", "#5d6b78", "#a8c2d4", "#7fa89c", "#c7a98a", "#9c6f5a",
           "#e3e1da", "#44484f", "#6d8fb0", "#b0855f", "#8fa3b8", "#c9a84a", "#3f5f8f", "#3f6a5c", "#c79a8f"]
LANDMARK_CITIES = ["Dubai", "New York", "New York", "Chicago", "Taipei", "New York", "Kuala Lumpur", "San Francisco",
                   "London", "Chicago", "Shanghai", "London"]
# Real-life facade colour of each tower, in the same order, plus a last entry for the low-rise block.
TINTS = ["#c3d0dd", "#d2c7ae", "#cfccc2", "#34363b", "#6fa497", "#a3bdd6", "#c9ced4", "#e8e6de", "#b0cadc",
         "#3a3d42", "#93b3c6", "#56808f", "#a0a5ac"]

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Playoff OPS City</title>
<style>
html,body{margin:0;height:100%;background:__BG__;color:#fff;font:13px/1.45 'Helvetica Neue',Arial,sans-serif}
body{display:flex;overflow:hidden}
#panel{flex:0 0 296px;box-sizing:border-box;padding:18px 16px 14px;background:__PANEL__;border-right:1px solid #1c2128;
  overflow-y:auto;display:flex;flex-direction:column;gap:13px}
#stage{flex:1;min-width:0;height:100vh;position:relative;
  background:linear-gradient(to bottom,#03050a 0%,#0a1224 48%,#1c2c4a 72%,#0e1626 100%)}
#stage canvas{display:block;width:100%;height:100%;cursor:grab}
#stage canvas:active{cursor:grabbing}
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
.notes{font-size:11px;margin-top:auto;padding-top:8px}
#card{position:fixed;left:0;top:0;z-index:20;display:none;pointer-events:none;max-width:300px;box-sizing:border-box;
  padding:10px 12px;background:#151a21;border:1px solid #3a4350;border-left:4px solid #3987e5;border-radius:4px;
  font:12px/1.5 Menlo,Consolas,monospace;color:#fff;box-shadow:0 6px 24px rgba(0,0,0,.55);will-change:transform}
#cat{display:none;position:fixed;inset:0;z-index:30;overflow-y:auto;background:__BG__;padding:0 24px 40px}
#cat header{position:sticky;top:0;z-index:1;display:flex;align-items:center;gap:16px;padding:14px 0;background:__BG__;border-bottom:1px solid #1c2128}
#cat h2{margin:0;font-size:18px;white-space:nowrap}#cat header p{flex:1;font-size:12px}
#cat h3{margin:22px 0 8px;font-size:14px;color:#dfe5ec}
.catgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.catgrid figure{margin:0;background:#0d131c;border:1px solid #232b36;border-bottom:4px solid #3987e5;border-radius:4px;cursor:pointer;overflow:hidden}
.catgrid figure:hover{border-color:#8b949e}
.catgrid img{display:block;width:100%;height:auto;background:#0d131c}
.catgrid figcaption{padding:6px 8px 8px;font-size:11px;line-height:1.4;color:__MUTED__}.catgrid b{color:#fff;font-size:12px}.catgrid i{color:#c9d1d9}
#fail{display:none;position:absolute;inset:0;padding:40px;font-size:15px}
@media (max-width:760px){body{flex-direction:column;overflow:auto}#panel{flex:none;border-right:0;border-bottom:1px solid #1c2128}
  #stage{flex:none;height:78vh}}
</style></head><body>
<aside id="panel">
  <h1>Every postseason offense, __START__–__END__</h1>
  <p>__N__ campaigns. Each building is one team's whole postseason, and its height is that team's OPS. The best offense of each year stands in front.</p>
  <div class="ctl"><span class="lab">View</span><div class="grp" data-key="view">
    <button data-v="city">City</button><button data-v="bars">Bars</button></div></div>
  <div><span class="lab">Colour key: how far the team went</span><ul id="key">__KEY__</ul><p id="keynote" style="font-size:11px;margin-top:4px"></p></div>
  <div class="ctl"><label for="org">Organization</label><select id="org"><option value="">All organizations</option>__ORG_OPTIONS__</select></div>
  <div class="ctl"><label for="season">Season</label><select id="season"><option value="">All seasons</option>__SEASON_OPTIONS__</select></div>
  <div class="ctl"><label for="ming">Minimum games: <span id="gval">1</span></label>
    <input type="range" id="ming" min="1" max="__MAX_G__" step="1" value="1"></div>
  <div class="ctl"><span class="lab">Postseason streak</span><div class="grp" data-key="streak">
    <button data-v="any">Any</button><button data-v="long">__STREAK__+ straight years</button></div></div>
  <div class="ctl"><span class="lab">Filtered-out buildings</span><div class="grp" data-key="others">
    <button data-v="fade">Faded</button><button data-v="hide">Hidden</button></div></div>
  <div><div id="count"></div><div class="grp" style="margin-top:6px"><button id="reset">Reset filters</button><button id="view">Reset view</button><button id="whole">Whole field</button></div>
    <div class="grp" style="margin-top:6px"><button id="catopen">Check every building</button></div></div>
  <p class="notes">Drag to orbit, scroll to zoom, right-drag or arrow keys to move along the streets, hover a building for details. The empty block is 1994, when no postseason was played.
  Height differences are drawn at twice their true size, measured from the median campaign; the ruler and hover cards show true OPS.
  In the City view every building is a simplified model of a different real tower, named on its hover card, and its highest point, spire included, is its height. The twelve best offenses with 8+ games get the detailed landmarks (__NAMELIST__); the rest follow their tower's overall form, crown, facade type and colour, not its exact proportions. Roughly, the better the OPS, the taller and better known the real tower. Which tower a campaign has, the lit windows, and the roads, traffic, people, parks and the plain dark low-rises without a plate carry no data; how far the team went is the colour of the plate under the building. The Bars view shows the same data as plain bars.<br><br>
  Data: Lahman Baseball Database (CC BY-SA 3.0) and the MLB Stats API.</p>
</aside>
<main id="stage"><div id="fail">This view needs WebGL, which this browser could not start.</div></main>
<div id="card" role="status"></div>
<section id="cat"><header><h2>Building catalog</h2><p id="catnote"></p><button id="catclose">Back to the city</button></header><div id="catbody"></div></section>
<script>__THREE__</script>
<script>__ORBIT__</script>
<script>
(function(){
var D=__DATA__, COLORS=__COLORS__, TICKS=__TICKS__;
var HS=__HS__, FOOT=__FOOT__, STOREY=__STOREY__, START=__START__, END=__END__, SLOTS=16, YEARS=END-START+1, BP=__PITCH__, CP=__CITY_PITCH__, RW=__RW__, SW=__SW__, PITCH=CP, LABELS=__LABELS__;
// Treat hex colours as sRGB, so materials match the colour key on screen
THREE.ColorManagement.legacyMode=false;
var stage=document.getElementById('stage'), renderer;
try{renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});}
catch(err){document.getElementById('fail').style.display='block';return;}
var DPR=Math.min(window.devicePixelRatio||1,1.5);renderer.setPixelRatio(DPR);
renderer.outputEncoding=THREE.sRGBEncoding;
renderer.setClearColor(0x070b14,1);
stage.appendChild(renderer.domElement);
var scene=new THREE.Scene();
scene.fog=new THREE.FogExp2(0x101a30,0.004);
// Everything laid out on the year x rank grid (ground, labels, ruler) lives in this group, stretched to the pitch
var field=new THREE.Group();field.scale.set(PITCH,1,PITCH);scene.add(field);
(function(){var c=document.createElement('canvas');c.width=2;c.height=256;var g=c.getContext('2d'),gr=g.createLinearGradient(0,0,0,256);
  gr.addColorStop(0,'#03050a');gr.addColorStop(0.48,'#0a1224');gr.addColorStop(0.72,'#1c2c4a');gr.addColorStop(1,'#0e1626');
  g.fillStyle=gr;g.fillRect(0,0,2,256);var t=new THREE.CanvasTexture(c);t.encoding=THREE.sRGBEncoding;scene.background=t;})();
var camera=new THREE.PerspectiveCamera(36,1,0.3,1700);
var controls=new THREE.OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;controls.dampingFactor=0.08;controls.maxPolarAngle=Math.PI/2-0.04;
controls.minDistance=1.2;controls.maxDistance=140*PITCH;controls.zoomSpeed=0.7;controls.screenSpacePanning=false;controls.listenToKeyEvents(window);controls.keyPanSpeed=28;
var sprites=[];
// The two views use different spacing: a full city block per campaign in the City view, tight rows in Bars.
function setPitch(p){PITCH=p;field.scale.set(p,1,p);controls.maxDistance=140*p;sprites.forEach(function(sp){sp.scale.y=sp.userData.size*p;});}
function homeView(){
  if(PITCH===CP){controls.target.set(YEARS*0.62*CP,1.4,-3.2*CP);camera.position.set(YEARS*0.62*CP-13,8.5,13);}   // City: among the towers
  else{camera.position.set((YEARS/2-2)*PITCH,28*PITCH,54*PITCH);controls.target.set((YEARS/2-0.5)*PITCH,0.5,-6*PITCH);}   // Bars: the whole field
  controls.update();}
function wholeField(){camera.position.set((YEARS/2-2)*PITCH,24*PITCH,50*PITCH);controls.target.set((YEARS/2-0.5)*PITCH,0.5,-6*PITCH);controls.update();}

scene.add(new THREE.HemisphereLight(0xc9dcff,0x1a2233,1.25));
scene.add(new THREE.AmbientLight(0xffffff,0.5));
var sun=new THREE.DirectionalLight(0xffffff,1.5);sun.position.set(-30,45,40);scene.add(sun);
var rim=new THREE.DirectionalLight(0x7fa6ff,0.7);rim.position.set(40,20,-50);scene.add(rim);

// ---------- procedural facades ----------
function rng(seed){return function(){seed|=0;seed=seed+0x6D2B79F5|0;var t=Math.imul(seed^seed>>>15,1|seed);
  t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
// One tile is 4 bays wide and 8 storeys tall. "map" is the daytime surface (tinted by the key
// colour); "glow" lights a random share of the windows.
function facade(style,seed){
  var W=128,H=256,cw=32,ch=32,r=rng(seed),a=document.createElement('canvas'),b=document.createElement('canvas');
  a.width=b.width=W;a.height=b.height=H;var m=a.getContext('2d'),g=b.getContext('2d'),x,y,lit;
  g.fillStyle='#000';g.fillRect(0,0,W,H);
  m.fillStyle=style===2?'#aeb9c8':style===3?'#dfe6ee':'#e4e8ee';m.fillRect(0,0,W,H);
  for(y=0;y<8;y++)for(x=0;x<4;x++){
    var wx,wy,ww,wh;
    if(style===0){wx=x*cw+7;wy=y*ch+7;ww=18;wh=19;}          // punched windows in masonry
    else if(style===1){wx=x*cw+1;wy=y*ch+9;ww=30;wh=15;}     // ribbon windows
    else if(style===2){wx=x*cw+2;wy=y*ch+3;ww=28;wh=25;}      // glass curtain wall
    else{wx=x*cw+4;wy=y*ch+1;ww=24;wh=27;}                    // floor-to-ceiling glass between steel fins
    lit=r()<(style===3?0.1:style===2?0.24:0.32);
    m.fillStyle=lit?'#f6ecd0':(style===3?'#6f8499':style===2?'#3d4a5e':'#27303d');m.fillRect(wx,wy,ww,wh);
    if(style===3){m.fillStyle='#8ea1b5';m.fillRect(wx+11,wy,2,wh);}
    if(lit){g.fillStyle=r()<0.75?'#ffd58a':'#cfe4ff';g.fillRect(wx,wy,ww,wh);}
    if(style===2){m.fillStyle='#8f9bab';m.fillRect(x*cw,y*ch+28,cw,4);}
  }
  function tex(c){var t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.encoding=THREE.sRGBEncoding;
    t.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());return t;}
  return {map:tex(a),glow:tex(b)};
}
var STYLES=__STYLES__,skins=[],s,g;
for(s=0;s<STYLES;s++)skins.push(facade(s,101+s*17));
// Towers wear their real-life colours, one entry per building type (the last is the low-rise block).
// How far the team went is the colour of the plate under each tower (PLATE) and of the bars.
var TINT=__TINTS__,WALL=[],ROOF=[],TRIM=[],PLATE=[];
for(g=0;g<TINT.length;g++){
  WALL.push([]);
  for(s=0;s<STYLES;s++)WALL[g].push(new THREE.MeshLambertMaterial({color:TINT[g],map:skins[s].map,emissive:0xffffff,
    emissiveMap:skins[s].glow,emissiveIntensity:0.9}));
  ROOF.push(new THREE.MeshLambertMaterial({color:new THREE.Color(TINT[g]).multiplyScalar(0.42)}));
  TRIM.push(new THREE.MeshLambertMaterial({color:new THREE.Color(TINT[g]).lerp(new THREE.Color(0xffffff),0.3)}));
}
for(g=0;g<COLORS.length;g++)PLATE.push(new THREE.MeshBasicMaterial({color:COLORS[g]}));
ROOF.concat(TRIM).forEach(function(m){m.userData.k=1;});PLATE.forEach(function(m){m.userData.k=2;});
var SOLID=new THREE.MeshLambertMaterial({vertexColors:true}),GLOW=new THREE.MeshBasicMaterial({vertexColors:true}),WHITE=new THREE.Color(1,1,1);
var STEEL=new THREE.MeshLambertMaterial({color:0x9aa4b2});
var BEACON=new THREE.MeshBasicMaterial({color:0xff3b30});
STEEL.userData.k=1;BEACON.userData.k=2;
var GHOST=new THREE.MeshBasicMaterial({color:0x6f86ad,transparent:true,opacity:0.05,depthWrite:false});

// ---------- building parts ----------
var UP=new THREE.Vector3(0,1,0),BAY=0.09,LOW=__LOW__,NAMES=__NAMES__;
// Facade per building type: 0 punched windows in masonry, 1 ribbon windows, 2 glass curtain wall
var SKIN=[3,0,0,1,2,2,1,0,2,1,2,2];
function bays(w){return Math.max(1,Math.round(w/BAY));}
function scaleUV(geo,u,v){var a=geo.attributes.uv,n;for(n=0;n<a.count;n++)a.setXY(n,a.getX(n)*u,a.getY(n)*v);}
function at(x,y,z,ry){return new THREE.Matrix4().compose(new THREE.Vector3(x||0,y,z||0),
  new THREE.Quaternion().setFromAxisAngle(UP,ry||0),new THREE.Vector3(1,1,1));}
// A building is collected as triangles per material (P), then merged into a single mesh.
function put(P,geo,mats,m){
  if(geo.index)geo=geo.toNonIndexed();
  if(m)geo.applyMatrix4(m);
  var pos=geo.attributes.position.array,nor=geo.attributes.normal.array,uv=geo.attributes.uv.array;
  var groups=geo.groups.length?geo.groups:[{start:0,count:pos.length/3,materialIndex:0}];
  groups.forEach(function(gr){
    var src=Array.isArray(mats)?(mats[gr.materialIndex]||mats[0]):mats,k=src.userData.k,mat=k===1?SOLID:k===2?GLOW:src,col=k?src.color:WHITE,b=null,i;
    for(i=0;i<P.length;i++)if(P[i].mat===mat)b=P[i];
    if(!b){b={mat:mat,p:[],n:[],u:[],c:[]};P.push(b);}
    for(i=gr.start;i<gr.start+gr.count;i++){b.p.push(pos[3*i],pos[3*i+1],pos[3*i+2]);
      b.n.push(nor[3*i],nor[3*i+1],nor[3*i+2]);b.u.push(uv[2*i],uv[2*i+1]);b.c.push(col.r,col.g,col.b);}
  });
}
function finish(P){
  var p=[],n=[],u=[],c=[],mats=[],geo=new THREE.BufferGeometry();
  P.forEach(function(b,i){geo.addGroup(p.length/3,b.p.length/3,i);mats.push(b.mat);p=p.concat(b.p);n=n.concat(b.n);u=u.concat(b.u);c=c.concat(b.c);});
  geo.setAttribute('color',new THREE.Float32BufferAttribute(c,3));
  geo.setAttribute('position',new THREE.Float32BufferAttribute(p,3));
  geo.setAttribute('normal',new THREE.Float32BufferAttribute(n,3));
  geo.setAttribute('uv',new THREE.Float32BufferAttribute(u,2));
  return new THREE.Mesh(geo,mats);
}
function box(P,d,wx,wz,y0,y1,ox,oz,ry,mat){
  var geo=new THREE.BoxGeometry(wx,y1-y0,wz);scaleUV(geo,bays(Math.max(wx,wz))/4,(y1-y0)/STOREY/8);
  var wall=mat||WALL[d.c][d.st],roof=mat||ROOF[d.c];
  put(P,geo,[wall,wall,roof,roof,wall,wall],at(ox,(y0+y1)/2,oz,ry));
}
function prism(P,d,r0,r1,y0,y1,sides,ox,oz,mat){
  var geo=new THREE.CylinderGeometry(r1,r0,y1-y0,sides,1,false);
  scaleUV(geo,Math.max(1,Math.round(Math.PI*(r0+r1)/BAY))/4,(y1-y0)/STOREY/8);
  put(P,geo,mat||[WALL[d.c][d.st],ROOF[d.c],ROOF[d.c]],at(ox,(y0+y1)/2,oz));
}
// Flat-shaded triangles (9 numbers each) around the building's axis; winding is fixed to face outwards.
function facets(P,mat,tris,uPer){
  var p=[],n=[],u=[],i,k,v=[new THREE.Vector3(),new THREE.Vector3(),new THREE.Vector3()],e=new THREE.Vector3(),f=new THREE.Vector3(),sw,a0,a;
  for(i=0;i<tris.length;i+=9){
    for(k=0;k<3;k++)v[k].set(tris[i+3*k],tris[i+3*k+1],tris[i+3*k+2]);
    e.subVectors(v[1],v[0]);f.subVectors(v[2],v[0]);e.cross(f).normalize();
    if(Math.abs(e.y)>0.99?e.y<0:e.x*(v[0].x+v[1].x+v[2].x)+e.z*(v[0].z+v[1].z+v[2].z)<0){sw=v[1];v[1]=v[2];v[2]=sw;e.negate();}
    a0=Math.atan2(v[0].z,v[0].x);
    for(k=0;k<3;k++){a=Math.atan2(v[k].z,v[k].x);if(a-a0>Math.PI)a-=2*Math.PI;if(a0-a>Math.PI)a+=2*Math.PI;
      p.push(v[k].x,v[k].y,v[k].z);n.push(e.x,e.y,e.z);u.push(a/(2*Math.PI)*uPer,v[k].y/STOREY/8);}
  }
  var geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.Float32BufferAttribute(p,3));
  geo.setAttribute('normal',new THREE.Float32BufferAttribute(n,3));
  geo.setAttribute('uv',new THREE.Float32BufferAttribute(u,2));
  put(P,geo,mat);
}
var SX=[1,-1,-1,1],SZ=[1,1,-1,-1];
// Four-sided tapering block: half-widths (ax, az) at the bottom, (bx, bz) at the top
function frustum(P,d,ax,az,bx,bz,y0,y1,mat){
  var t=[],c=[],i,j;
  for(i=0;i<4;i++){j=(i+1)%4;
    t.push(SX[i]*ax,y0,SZ[i]*az, SX[j]*ax,y0,SZ[j]*az, SX[j]*bx,y1,SZ[j]*bz,
           SX[i]*ax,y0,SZ[i]*az, SX[j]*bx,y1,SZ[j]*bz, SX[i]*bx,y1,SZ[i]*bz);}
  facets(P,mat||WALL[d.c][d.st],t,Math.max(1,Math.round(2*(ax+az+bx+bz)/BAY))/4);
  c.push(bx,y1,bz, bx,y1,-bz, -bx,y1,-bz, bx,y1,bz, -bx,y1,-bz, -bx,y1,bz);
  facets(P,mat||ROOF[d.c],c,1);
}
function spike(P,mat,r,y0,y1,sides,ox,oz){
  put(P,new THREE.ConeGeometry(r,y1-y0,sides,1),mat,at(ox,(y0+y1)/2,oz,sides===4?Math.PI/4:0));
}
var MS=1;   // mast scale: below 1 for scaled-down short buildings
function mast(P,y0,y1,ox,oz,r){
  r=(r||0.012)*MS;
  put(P,new THREE.CylinderGeometry(r*0.5,r*1.6,y1-y0,6),STEEL,at(ox,(y0+y1)/2,oz));
  put(P,new THREE.SphereGeometry(0.028*MS,8,6),BEACON,at(ox,y1-0.028*MS,oz));
}
// The plate under every tower carries the result colour.
function plate(P,d){put(P,new THREE.BoxGeometry(0.94,0.035,0.94),PLATE[d.g],at(0,0.0175,0));return P;}
function round(P,d,r,y0,y1,ox,oz,sides){   // upright round column with windows
  var geo=new THREE.CylinderGeometry(r,r,y1-y0,sides||10,1,false);
  scaleUV(geo,Math.max(1,Math.round(2*Math.PI*r/BAY))/4,(y1-y0)/STOREY/8);
  put(P,geo,[WALL[d.c][d.st],ROOF[d.c],ROOF[d.c]],at(ox,(y0+y1)/2,oz));
}
// ---------- one-of-a-kind buildings ----------
// Every campaign outside the twelve landmarks is modelled on its own real tower (d.bn). The tower's traits
// d.b = [form, crown, facade, colour, sides] come from real_towers.py; only the finer proportions are drawn
// from a random stream seeded by the campaign. Short buildings are scaled-down towers, not squat blocks.
function crown(P,d,kind,cw,B,H,ox,oz){
  var h=H-B,t,pts=[];
  switch(kind){
    case 0: box(P,d,cw*1.2,cw*1.2,B,H,ox,oz,0,ROOF[d.c]);break;                       // plant room
    case 1: mast(P,B,H,ox,oz,0.014);break;                                             // mast
    case 2: mast(P,B,H,ox-cw*0.4,oz);mast(P,B,B+h*0.8,ox+cw*0.4,oz);break;             // twin antennas
    case 3: spike(P,TRIM[d.c],cw*Math.SQRT2,B,H,4,ox,oz);break;                        // pyramid
    case 4:                                                                            // steel crown and needle
      for(t=0;t<5;t++)prism(P,d,cw*Math.sqrt(1-Math.pow(t/5*0.95,2)),cw*Math.sqrt(1-Math.pow((t+1)/5*0.95,2)),
        B+h*0.6*t/5,B+h*0.6*(t+1)/5,8,ox,oz,STEEL);
      spike(P,STEEL,cw*0.312,B+h*0.6,H,8,ox,oz);break;
    case 5: box(P,d,cw*1.4,cw*1.4,B,B+h*0.3,ox,oz);box(P,d,cw*0.9,cw*0.9,B+h*0.3,B+h*0.55,ox,oz);   // stepped top and mast
      mast(P,B+h*0.55,H,ox,oz);break;
    case 6: for(t=0;t<=8;t++)pts.push(new THREE.Vector2(Math.max(0,cw*Math.cos(t/8*Math.PI/2)),B+h*Math.sin(t/8*Math.PI/2)));   // dome
      put(P,new THREE.LatheGeometry(pts,12),TRIM[d.c],at(ox,0,oz));break;
    default: spike(P,STEEL,cw*0.8,B,H,12,ox,oz);                                       // round spire
  }
}
function generate(P,d,H){
  MS=H<LOW?Math.max(0.3,H/LOW):1;
  var r=rng(d.i*7919+101),w=FOOT*(0.8+0.5*r())*MS,q=w/2,i,j,t,n,y,y1,ax,az,a,k,s,geo,pos,rad,tris,spots=[[0,0]],cw=q*0.5;
  d.c=13+d.b[3];d.st=d.b[2];
  var body=d.b[0],kind=d.b[1],B=kind===0?H*(0.95+0.03*r()):H*(0.94-0.16*r());
  switch(body){
    case 0: // rectangular setbacks
      n=2+Math.floor(r()*4);ax=q;az=q*(0.6+0.4*r());y=0;
      for(t=0;t<n;t++){y1=t===n-1?B:y+(B-y)*(0.3+0.4*r());box(P,d,2*ax,2*az,y,y1);y=y1;cw=Math.min(ax,az);ax*=0.6+0.3*r();az*=0.6+0.3*r();}
      cw*=0.7;break;
    case 1: // tapering slab
      az=q*(0.6+0.4*r());k=0.3+0.6*r();frustum(P,d,q,az,q*k,az*k,0,B);cw=Math.min(q,az)*k*0.8;break;
    case 2: // polygonal or round tiers
      s=d.b[4]||[6,8][Math.floor(r()*2)];n=1+Math.floor(r()*3);rad=q;y=0;
      for(t=0;t<n;t++){y1=t===n-1?B:y+(B-y)*(0.35+0.4*r());k=0.8+0.2*r();prism(P,d,rad,rad*k,y,y1,s);y=y1;cw=rad*k;rad=cw*(0.6+0.3*r());}
      cw*=0.7;break;
    case 3: // twisting lobed tower
      var lobes=2+Math.floor(r()*4),twist=(r()-0.5)*5,taper=0.1+0.3*r(),amp=0.05+0.1*r();
      geo=new THREE.CylinderGeometry(1,1,B,24,14,false);pos=geo.attributes.position;
      for(i=0;i<pos.count;i++){rad=Math.hypot(pos.getX(i),pos.getZ(i));if(rad<1e-6)continue;
        s=pos.getY(i)/B+0.5;a=Math.atan2(pos.getZ(i),pos.getX(i));
        rad=w*(0.5-taper*s)*(1+amp*Math.cos(lobes*(a-twist*s)));pos.setX(i,Math.cos(a)*rad);pos.setZ(i,Math.sin(a)*rad);}
      geo.computeVertexNormals();scaleUV(geo,bays(w*2.5)/4,B/STOREY/8);
      put(P,geo,[WALL[d.c][d.st],ROOF[d.c],ROOF[d.c]],at(0,B/2,0));cw=w*(0.5-taper)*(1-amp)*0.6;break;
    case 4: // bundled tubes of different heights
      n=2+Math.floor(r()*2);k=Math.floor(r()*n*n);
      for(i=0;i<n;i++)for(j=0;j<n;j++){ax=(j-(n-1)/2)*w/n;az=(i-(n-1)/2)*w/n;
        box(P,d,w/n,w/n,0,i*n+j===k?B:B*(0.45+0.5*r()),ax,az);if(i*n+j===k)spots=[[ax,az]];}
      cw=w/n*0.4;break;
    case 5: // wings stepping back around a core
      var nw=3+Math.floor(r()*2),T=3+Math.floor(r()*5),rc=w*0.16,W0=w*(0.18+0.08*r()),top=B*(0.8+0.15*r()),a0=r()*Math.PI,len;
      for(i=0;i<nw;i++){a=a0+i*2*Math.PI/nw;
        for(t=0;t<T;t++){y=t?top*(nw*(t-1)+i+1)/(nw*T):0;y1=top*(nw*t+i+1)/(nw*T);len=rc+(w*0.62-rc)*(1-t/T);
          box(P,d,len,W0*(1-0.3*t/T),y,y1,Math.cos(a)*len/2,-Math.sin(a)*len/2,a);}}
      prism(P,d,rc,rc,0,B,nw===3?6:8);cw=rc*0.8;break;
    case 6: // rounded tower that closes to a tip (needs no crown)
      var p0=0.12+0.3*r(),ex=0.5+0.6*r();pos=[];
      for(i=0;i<=16;i++){s=i/16;pos.push(new THREE.Vector2(q*Math.pow(Math.sin(Math.PI*(p0+(1-p0)*s)),ex),s*H));}
      geo=new THREE.LatheGeometry(pos,20);scaleUV(geo,bays(w*2.8)/4,H/STOREY/8);put(P,geo,WALL[d.c][d.st]);return;
    case 7: // twin towers joined by a bridge
      rad=w*0.2;a=w*0.27;k=r()<0.5;y=B*(0.3+0.4*r());
      for(i=-1;i<2;i+=2){if(k)round(P,d,rad,0,B,i*a,0,12);else box(P,d,rad*1.8,rad*1.8,0,B,i*a,0);}
      box(P,d,a*2,rad*0.4,y,y+B*0.03,0,0,0,TRIM[d.c]);spots=[[-a,0],[a,0]];cw=rad*0.7;break;
    case 8: // square base turning into eight triangles
      y=B*(0.05+0.15*r());box(P,d,w,w,0,y);tris=[];
      var TX=[0,-q,0,q],TZ=[q,0,-q,0];
      for(i=0;i<4;i++){j=(i+1)%4;
        tris.push(SX[i]*q,y,SZ[i]*q, SX[j]*q,y,SZ[j]*q, TX[i],B,TZ[i],  TX[i],B,TZ[i], TX[j],B,TZ[j], SX[j]*q,y,SZ[j]*q);}
      facets(P,WALL[d.c][d.st],tris,bays(w*3.4)/4);
      box(P,d,q*Math.SQRT2,q*Math.SQRT2,B-H*0.01,B,0,0,Math.PI/4,TRIM[d.c]);cw=q*0.5;break;
    case 10: // plain box or slab
      az=q*(0.55+0.45*r());box(P,d,2*q,2*az,0,B);cw=Math.min(q,az)*0.6;break;
    default: // flared tiers on a base
      n=4+Math.floor(r()*6);y=B*(0.1+0.15*r());k=0.55+0.2*r();frustum(P,d,q,q,q*(k+0.15),q*(k+0.15),0,y);
      for(t=0;t<n;t++)frustum(P,d,q*k,q*k,q*(k+0.14),q*(k+0.14),y+(B-y)*t/n,y+(B-y)*(t+1)/n);cw=q*k*0.6;
  }
  spots.forEach(function(o){crown(P,d,kind,cw,B,H,o[0],o[1]);});
}
// Each landmark type is a simplified model of a real tower. Every one ends with its highest point exactly at H.
function build(d){
  var P=[],H=d.h*HS,w=FOOT,q=w/2,i,j,t,a,y0,y1,r,s,geo,tris,pos;
  MS=1;if(d.k<0){generate(P,d,H);return finish(plate(P,d));}
  d.st=SKIN[d.k];d.c=d.k;
  if(H<LOW){d.low=1;d.st=d.k%3;d.c=NAMES.length;box(P,d,w,w,0,H);return finish(plate(P,d));}   // too short to model: a low-rise block
  switch(d.k){
    case 0: // Burj Khalifa. Y-shaped plan: three wings 120 degrees apart around a hexagonal core.
      // Each wing steps back nine times, the wings taking turns, so the 27 setbacks spiral upwards.
      // The core outlasts the wings, steps in twice more and ends in a telescoping steel spire.
      var T=9,L0=w*0.66,W0=w*0.2,rc=w*0.14,top=H*0.72,len,wid,cx,cz;
      for(i=0;i<3;i++){a=i*2*Math.PI/3+Math.PI/2;cx=Math.cos(a);cz=-Math.sin(a);
        for(t=0;t<T;t++){
          y0=t?H*(0.1+0.62*(3*(t-1)+i)/(3*T-1)):0;y1=H*(0.1+0.62*(3*t+i)/(3*T-1));
          len=rc+(L0-rc)*(1-t/T);wid=W0*(1-0.3*t/T);
          box(P,d,len-wid/2,wid,y0,y1,cx*(len-wid/2)/2,cz*(len-wid/2)/2,a);   // wing
          round(P,d,wid/2,y0,y1,cx*(len-wid/2),cz*(len-wid/2));               // its rounded nose
          if(t<T-1)put(P,new THREE.CylinderGeometry(wid*0.18,wid*0.18,H*0.012,6),STEEL,at(cx*(len-wid*0.7),y1+H*0.006,cz*(len-wid*0.7)));
        }
        if(i<2)box(P,d,w*0.3,w*0.16,0,H*0.03,Math.cos(a+Math.PI/3)*w*0.3,-Math.sin(a+Math.PI/3)*w*0.3,a+Math.PI/3,TRIM[d.c]);  // entry pavilions
      }
      prism(P,d,rc,rc,0,top,6);prism(P,d,rc*0.82,rc*0.82,top,H*0.765,6);prism(P,d,rc*0.64,rc*0.64,H*0.765,H*0.8,6);
      prism(P,d,rc*0.46,rc*0.4,H*0.8,H*0.845,6,0,0,STEEL);prism(P,d,rc*0.32,rc*0.22,H*0.845,H*0.9,6,0,0,STEEL);
      prism(P,d,rc*0.16,rc*0.1,H*0.9,H*0.95,6,0,0,STEEL);spike(P,STEEL,rc*0.08,H*0.95,H-0.02,6);
      put(P,new THREE.SphereGeometry(0.02,8,6),BEACON,at(0,H-0.02,0));break;
    case 1: // Empire State Building: base, shouldered shaft, setbacks, mooring mast
      box(P,d,w,w,0,H*0.05);box(P,d,w*0.86,w*0.7,H*0.05,H*0.2);box(P,d,w*0.82,w*0.34,H*0.2,H*0.6);
      box(P,d,w*0.64,w*0.5,H*0.2,H*0.74);box(P,d,w*0.5,w*0.4,H*0.74,H*0.8);box(P,d,w*0.36,w*0.3,H*0.8,H*0.85);
      prism(P,d,w*0.1,w*0.07,H*0.85,H*0.9,8,0,0,TRIM[d.c]);prism(P,d,w*0.06,w*0.03,H*0.9,H*0.94,8,0,0,TRIM[d.c]);
      mast(P,H*0.94,H);break;
    case 2: // Chrysler Building: slim shaft, curved steel crown, needle
      box(P,d,w,w,0,H*0.07);box(P,d,w*0.7,w*0.7,H*0.07,H*0.2);box(P,d,w*0.56,w*0.56,H*0.2,H*0.68);
      box(P,d,w*0.48,w*0.48,H*0.68,H*0.73);
      for(t=0;t<6;t++){s=t/6*0.95;r=(t+1)/6*0.95;
        frustum(P,d,w*0.24*Math.sqrt(1-s*s),w*0.24*Math.sqrt(1-s*s),w*0.24*Math.sqrt(1-r*r),w*0.24*Math.sqrt(1-r*r),
          H*(0.73+0.17*t/6),H*(0.73+0.17*(t+1)/6),STEEL);}
      spike(P,STEEL,w*0.24*Math.sqrt(1-0.95*0.95)*Math.SQRT2,H*0.9,H,4);break;
    case 3: // Willis Tower: nine bundled tubes ending at four heights, twin antennas
      var roof=H*0.84,fl=[50,90,66, 108,108,90, 66,90,50];
      for(i=0;i<3;i++)for(j=0;j<3;j++)box(P,d,w/3,w/3,0,roof*fl[i*3+j]/108,(j-1)*w/3,(i-1)*w/3);
      box(P,d,w*0.3,w*0.2,roof,H*0.87,-w/6,0,0,ROOF[d.c]);mast(P,H*0.87,H,-w/4,0);mast(P,H*0.87,H*0.975,-w/12,0);break;
    case 4: // Taipei 101: tapering base, eight flared tiers, spire
      frustum(P,d,q,q,q*0.78,q*0.78,0,H*0.19);
      for(t=0;t<8;t++)frustum(P,d,q*0.6,q*0.6,q*0.74,q*0.74,H*(0.19+0.08*t),H*(0.19+0.08*(t+1)));
      box(P,d,w*0.44,w*0.44,H*0.83,H*0.87);box(P,d,w*0.28,w*0.28,H*0.87,H*0.9);
      prism(P,d,w*0.05,w*0.03,H*0.9,H*0.93,8,0,0,TRIM[d.c]);mast(P,H*0.93,H);break;
    case 5: // One World Trade Center: square base turning into eight tall triangles, mast
      box(P,d,w,w,0,H*0.12);tris=[];y0=H*0.12;y1=H*0.87;
      var TX=[0,-q,0,q],TZ=[q,0,-q,0];
      for(i=0;i<4;i++){j=(i+1)%4;
        tris.push(SX[i]*q,y0,SZ[i]*q, SX[j]*q,y0,SZ[j]*q, TX[i],y1,TZ[i],  TX[i],y1,TZ[i], TX[j],y1,TZ[j], SX[j]*q,y0,SZ[j]*q);}
      facets(P,WALL[d.c][d.st],tris,bays(w*3.4)/4);
      box(P,d,q*Math.SQRT2,q*Math.SQRT2,H*0.87,H*0.885,0,0,Math.PI/4,TRIM[d.c]);
      prism(P,d,w*0.12,w*0.12,H*0.885,H*0.9,12,0,0,STEEL);mast(P,H*0.9,H,0,0,0.018);break;
    case 6: // Petronas Towers: twin round towers, skybridge, pinnacles
      box(P,d,w,w*0.5,0,H*0.04);
      for(i=-1;i<2;i+=2){a=i*w*0.27;r=w*0.21;
        prism(P,d,r,r,H*0.04,H*0.68,12,a,0);prism(P,d,r*0.86,r*0.86,H*0.68,H*0.76,12,a,0);
        prism(P,d,r*0.7,r*0.7,H*0.76,H*0.82,12,a,0);prism(P,d,r*0.52,r*0.52,H*0.82,H*0.86,12,a,0);
        prism(P,d,r*0.52,r*0.15,H*0.86,H*0.92,12,a,0,TRIM[d.c]);mast(P,H*0.92,H,a,0);}
      box(P,d,w*0.3,w*0.05,H*0.4,H*0.425,0,0,0,TRIM[d.c]);break;
    case 7: // Transamerica Pyramid: four-sided pyramid with two wings and a clad spire
      frustum(P,d,q,q,q*0.27,q*0.27,0,H*0.75);
      box(P,d,q*0.25,q*0.3,H*0.5,H*0.73,q*0.41,0,0,TRIM[d.c]);box(P,d,q*0.25,q*0.3,H*0.5,H*0.73,-q*0.41,0,0,TRIM[d.c]);
      spike(P,TRIM[d.c],q*0.27*Math.SQRT2,H*0.75,H,4);break;
    case 8: // The Shard: glass pyramid ending in open shards
      frustum(P,d,q,q*0.9,q*0.13,q*0.11,0,H*0.9);
      spike(P,TRIM[d.c],w*0.045,H*0.86,H,4,-w*0.03,0);spike(P,TRIM[d.c],w*0.04,H*0.86,H*0.96,4,w*0.035,w*0.01);break;
    case 9: // John Hancock Center: tapering slab with twin antennas
      frustum(P,d,q,q*0.72,q*0.62,q*0.44,0,H*0.89);
      box(P,d,q*0.9,q*0.6,H*0.89,H*0.915,0,0,0,ROOF[d.c]);mast(P,H*0.915,H,-w*0.1,0);mast(P,H*0.915,H*0.98,w*0.1,0);break;
    case 10: // Shanghai Tower: rounded triangle that twists and narrows as it rises
      geo=new THREE.CylinderGeometry(1,1,H,24,14,false);pos=geo.attributes.position;
      for(i=0;i<pos.count;i++){r=Math.hypot(pos.getX(i),pos.getZ(i));if(r<1e-6)continue;
        s=pos.getY(i)/H+0.5;a=Math.atan2(pos.getZ(i),pos.getX(i));
        r=w*(0.5-0.2*s)*(1+0.13*Math.cos(3*(a-2.1*s)));pos.setX(i,Math.cos(a)*r);pos.setZ(i,Math.sin(a)*r);}
      geo.computeVertexNormals();scaleUV(geo,bays(w*2.5)/4,H/STOREY/8);
      put(P,geo,[WALL[d.c][d.st],ROOF[d.c],ROOF[d.c]],at(0,H/2,0));break;
    default: // 30 St Mary Axe (the Gherkin): bulging round tower with a domed tip
      pos=[];for(i=0;i<=16;i++){s=i/16;pos.push(new THREE.Vector2(w*0.5*Math.pow(Math.sin(Math.PI*(0.3+0.7*s)),0.7),s*H));}
      geo=new THREE.LatheGeometry(pos,20);scaleUV(geo,bays(w*2.8)/4,H/STOREY/8);
      put(P,geo,WALL[d.c][d.st]);
  }
  return finish(plate(P,d));
}
var builds=[],bars=[],pick=[],FLAT=COLORS.map(function(c){return new THREE.MeshLambertMaterial({color:new THREE.Color(c).multiplyScalar(0.5)});});
D.forEach(function(d,ix){
  d.i=ix;var m=build(d);m.position.set((d.y-START)*CP,0,-d.s*CP);m.userData.ix=ix;m.userData.mat=m.material;scene.add(m);builds.push(m);
  var H=d.h*HS,b=new THREE.Mesh(new THREE.BoxGeometry(FOOT,H,FOOT),FLAT[d.g]);
  b.position.set((d.y-START)*BP,H/2,-d.s*BP);b.userData.ix=ix;b.userData.mat=b.material;scene.add(b);bars.push(b);
});

// ---------- ground, labels, ruler ----------
function canvasTexture(w,h,paint){var c=document.createElement('canvas');c.width=w;c.height=h;paint(c.getContext('2d'),w,h);
  var t=new THREE.CanvasTexture(c);t.encoding=THREE.sRGBEncoding;t.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());return t;}
// One city block per cell, drawn to scale: road (two lanes each way), kerb, pavement, paved plaza.
// The cell edge is the centre line of the road, so neighbouring cells join into full roads and crossings.
var block=canvasTexture(1024,1024,function(c){
  c.scale(2,2);var k=512/CP,r=RW*k,s=(RW+SW)*k,n,E=512;
  c.fillStyle='#1b222c';c.fillRect(0,0,E,E);                                              // plaza paving
  c.fillStyle='#212936';for(n=s;n<E-s;n+=16){c.fillRect(n,s,1,E-2*s);c.fillRect(s,n,E-2*s,1);}
  c.fillStyle='#3a4350';c.fillRect(0,0,E,s);c.fillRect(0,E-s,E,s);c.fillRect(0,0,s,E);c.fillRect(E-s,0,s,E);   // pavement
  c.fillStyle='#0c0f14';c.fillRect(0,0,E,r);c.fillRect(0,E-r,E,r);c.fillRect(0,0,r,E);c.fillRect(E-r,0,r,E);   // asphalt
  c.fillStyle='#5d6878';c.fillRect(r,r,E-2*r,1.5);c.fillRect(r,E-r-1.5,E-2*r,1.5);c.fillRect(r,r,1.5,E-2*r);c.fillRect(E-r-1.5,r,1.5,E-2*r);   // kerb
  c.fillStyle='#aab2be';for(n=s+10;n<E-s-12;n+=14){c.fillRect(n,r/2,7,1);c.fillRect(n,E-r/2-1,7,1);c.fillRect(r/2,n,1,7);c.fillRect(E-r/2-1,n,1,7);}   // lane dashes
  c.fillStyle='#c9a227';c.fillRect(s,0,E-2*s,1.3);c.fillRect(s,E-1.3,E-2*s,1.3);c.fillRect(0,s,1.3,E-2*s);c.fillRect(E-1.3,s,1.3,E-2*s);            // centre line
  c.fillStyle='#d7dde6';
  [r+2,E-s+2].forEach(function(x0){var w=s-r-4;                                           // zebra crossings in line with the pavements
    for(n=2;n<r-2;n+=5){c.fillRect(x0,n,w,2.5);c.fillRect(x0,E-n-2.5,w,2.5);c.fillRect(n,x0,2.5,w);c.fillRect(E-n-2.5,x0,2.5,w);}});
  [s+3,E-s-4.5].forEach(function(x0){c.fillRect(x0,0,1.5,r);c.fillRect(x0,E-r,1.5,r);c.fillRect(0,x0,r,1.5);c.fillRect(E-r,x0,r,1.5);});   // stop lines
});
block.wrapS=block.wrapT=THREE.RepeatWrapping;block.repeat.set(YEARS+2,SLOTS+2);
var grid=canvasTexture(64,64,function(c){c.fillStyle='#0f141b';c.fillRect(0,0,64,64);c.fillStyle='#232b36';c.fillRect(0,0,64,1);c.fillRect(0,0,1,64);});
grid.wrapS=grid.wrapT=THREE.RepeatWrapping;grid.repeat.set(YEARS+2,SLOTS+2);
var STREETS=new THREE.MeshLambertMaterial({map:block}),PLAIN=new THREE.MeshLambertMaterial({map:grid});
var ground=new THREE.Mesh(new THREE.PlaneGeometry(YEARS+2,SLOTS+2),STREETS);
ground.rotation.x=-Math.PI/2;ground.position.set((YEARS-1)/2,0,-(SLOTS+1)/2);field.add(ground);
var apron=new THREE.Mesh(new THREE.PlaneGeometry(5000,5000),new THREE.MeshBasicMaterial({color:0x070a10,fog:false}));
apron.rotation.x=-Math.PI/2;apron.position.set((YEARS-1)/2*CP,-0.25,-(SLOTS+1)/2*CP);scene.add(apron);
var CELL=64,strip=canvasTexture(YEARS*CELL,72,function(c,w,h){
  c.clearRect(0,0,w,h);c.font='600 23px Menlo,Consolas,monospace';c.textAlign='center';c.textBaseline='middle';
  for(var y=0;y<YEARS;y++){c.fillStyle=(START+y)===1994?'#5b6470':'#c3ccd8';c.fillText(String(START+y),y*CELL+CELL/2,h/2);}
});
var years=new THREE.Mesh(new THREE.PlaneGeometry(YEARS,1.1),new THREE.MeshBasicMaterial({map:strip,transparent:true,fog:false}));
years.rotation.x=-Math.PI/2;years.position.set((YEARS-1)/2,0.04,0.75);field.add(years);
function label(text,x,y,z,size){
  var t=canvasTexture(256,96,function(c){c.font='600 44px Menlo,Consolas,monospace';c.textAlign='center';c.textBaseline='middle';
    c.fillStyle='#c3ccd8';c.fillText(text,128,48);});
  var sp=new THREE.Sprite(new THREE.SpriteMaterial({map:t,transparent:true,fog:false,depthWrite:false}));
  sp.scale.set(size*2.67,size*PITCH,1);sp.userData.size=size;sprites.push(sp);sp.position.set(x,y,z);field.add(sp);
}
var line=new THREE.LineBasicMaterial({color:0x35435a,transparent:true,opacity:0.8}),pts=[],top=TICKS[TICKS.length-1][1]*HS+0.6;
TICKS.forEach(function(t){
  var y=t[1]*HS;
  pts.push(new THREE.Vector3(-1.5,y,-(SLOTS+1)),new THREE.Vector3(YEARS+0.5,y,-(SLOTS+1)));   // back wall guide
  pts.push(new THREE.Vector3(-1.5,y,-(SLOTS+1)),new THREE.Vector3(-1.5,y,0));                   // left wall guide
  label(t[0],-3.0,y,-(SLOTS+1),1.05);
});
pts.push(new THREE.Vector3(-1.5,0,0),new THREE.Vector3(-1.5,top,0),new THREE.Vector3(-1.5,0,-(SLOTS+1)),new THREE.Vector3(-1.5,top,-(SLOTS+1)));
field.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(pts),line));
label('OPS',-3.0,top+0.5,-(SLOTS+1),1.05);
[1977,1980,1985,1990,1995,2000,2005,2010,2015,2020,2026].forEach(function(y){label(String(y),y-START,0.5,2.9,0.9);});

// ---------- city life: traffic, people, trees, lamps, signals, background low-rises (decoration only) ----------
// Roads run along the cell boundaries of the ground texture, two lanes each way (RW = half the road width).
// Cars keep to their lane on the right, queue behind each other and stop at red lights; people walk the pavements.
var life=new THREE.Group();scene.add(life);
var NX=YEARS+2,NZ=SLOTS+2,LX=NX*CP,LZ=NZ*CP,X0=-1.5*CP,ZA=0.5*CP,lr=rng(4242),dummy=new THREE.Object3D(),tmpC=new THREE.Color();
function fleet(n,geo,mat,moving){var m=new THREE.InstancedMesh(geo,mat,Math.max(1,n));m.count=n;if(moving)m.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  m.frustumCulled=false;life.add(m);return m;}
var lanes=[],LANE=[RW*0.25,RW*0.75],STOP=RW+SW+0.1,NC=0;
function addLanes(ew,count,len){var j,d,l,s,L;
  for(j=1;j<count;j++)for(d=-1;d<2;d+=2)for(l=0;l<2;l++){L={ew:ew,line:j*CP,dir:d,off:LANE[l],len:len,n:Math.round(len/CP),cars:[]};
    for(s=lr()*20;s<len-1;s+=8+lr()*44)L.cars.unshift({s:s,v:0,vmax:0.42+0.3*lr(),ix:NC++});   // leader first
    lanes.push(L);}}
addLanes(true,NZ,LX);    // streets: z = ZA - j*CP
addLanes(false,NX,LZ);   // avenues: x = X0 + j*CP
var cars=fleet(NC,new THREE.BoxGeometry(0.135,0.036,0.056).translate(0,0.03,0),new THREE.MeshLambertMaterial({}),1);
var cabs=fleet(NC,new THREE.BoxGeometry(0.07,0.026,0.05).translate(-0.008,0.06,0),new THREE.MeshLambertMaterial({color:0x18202c}),1);
var heads=fleet(NC,new THREE.BoxGeometry(0.007,0.012,0.048).translate(0.069,0.032,0),new THREE.MeshBasicMaterial({color:0xfff1c0}),1);
var tails=fleet(NC,new THREE.BoxGeometry(0.007,0.01,0.048).translate(-0.069,0.032,0),new THREE.MeshBasicMaterial({color:0xff2a1a}),1);
var PAINT=[0xd9dde3,0x20242b,0x8b9099,0xb3261e,0x1f4e9c,0xf2f2f2,0x2e6b4a,0x6b7a8c],CLOTH=[0xc8433a,0x3a6fc8,0xe0c04a,0x4aa36b,0xdddddd,0x333a48,0xb86bc4,0xe08a3a],SKIN_TONES=[0xf1c9a5,0xd9a47a,0xa9744f,0x7a4d32,0x5a3a26];
(function(){for(var i=0;i<NC;i++)cars.setColorAt(i,tmpC.set(lr()<0.1?0xf0c020:PAINT[Math.floor(lr()*PAINT.length)]));})();
var GREEN=0x35e06a,AMBER=0xffb020,RED=0xff3020,sigEW=new THREE.MeshBasicMaterial({color:GREEN}),sigNS=new THREE.MeshBasicMaterial({color:RED});
function traffic(dt,t){
  var cyc=t%14,goEW=cyc<5.5,goNS=cyc>=7&&cyc<12.5,i,j,L,c,n,lim,k,d,want,ns,x,z,rot,q;
  sigEW.color.setHex(goEW?GREEN:cyc<6.5?AMBER:RED);sigNS.color.setHex(goNS?GREEN:cyc>=12.5&&cyc<13.5?AMBER:RED);
  for(i=0;i<lanes.length;i++){L=lanes[i];n=L.cars.length;
    for(j=0;j<n;j++){c=L.cars[j];
      lim=(j===0?L.cars[n-1].s+L.len:L.cars[j-1].s)-0.23;                         // stay behind the car in front
      if(!(L.ew?goEW:goNS)){k=Math.ceil((c.s+STOP-0.03)/CP);if(k>=1&&k<=L.n-1)lim=Math.min(lim,k*CP-STOP);}   // red light: next stop line
      d=lim-c.s;want=d>0.6?c.vmax:d>0.004?Math.max(0.04,c.vmax*d/0.6):0;
      c.v+=(want-c.v)*Math.min(1,dt*5);ns=c.s+c.v*dt;if(ns>lim)ns=Math.max(c.s,lim);c.s=ns;
      q=L.dir>0?c.s:L.len-c.s;
      if(L.ew){x=X0+q;z=ZA-L.line+L.dir*L.off;rot=L.dir>0?0:Math.PI;}
      else{z=ZA-q;x=X0+L.line+L.dir*L.off;rot=L.dir>0?Math.PI/2:-Math.PI/2;}
      dummy.position.set(x,0,z);dummy.rotation.y=rot;dummy.updateMatrix();
      cars.setMatrixAt(c.ix,dummy.matrix);cabs.setMatrixAt(c.ix,dummy.matrix);heads.setMatrixAt(c.ix,dummy.matrix);tails.setMatrixAt(c.ix,dummy.matrix);}
    if(n&&L.cars[0].s>=L.len){c=L.cars.shift();c.s-=L.len;L.cars.push(c);}
  }
  cars.instanceMatrix.needsUpdate=cabs.instanceMatrix.needsUpdate=heads.instanceMatrix.needsUpdate=tails.instanceMatrix.needsUpdate=true;
}
// People: each walks one pavement (0.27 from the road centre) end to end
var NP=1600,peds=[],bodies=fleet(NP,new THREE.BoxGeometry(0.014,0.034,0.011).translate(0,0.017,0),new THREE.MeshLambertMaterial({}),1);
var faces=fleet(NP,new THREE.OctahedronGeometry(0.009,1).translate(0,0.042,0),new THREE.MeshLambertMaterial({}),1);
(function(){var i,ew;for(i=0;i<NP;i++){ew=lr()<0.5;
  peds.push({ew:ew,line:(1+Math.floor(lr()*((ew?NZ:NX)-1)))*CP,side:(lr()<0.5?1:-1)*(RW+SW*(0.25+0.5*lr())),dir:lr()<0.5?1:-1,s:lr(),v:0.03+0.035*lr(),ph:lr()*6.28});
  bodies.setColorAt(i,tmpC.set(CLOTH[Math.floor(lr()*CLOTH.length)]));faces.setColorAt(i,tmpC.set(SKIN_TONES[Math.floor(lr()*SKIN_TONES.length)]));}})();
function walk(t){
  var i,p,len,q;
  for(i=0;i<NP;i++){p=peds[i];len=p.ew?LX:LZ;q=((p.s+t*p.v/len)%1)*len;if(p.dir<0)q=len-q;
    if(p.ew){dummy.position.set(X0+q,Math.abs(Math.sin(t*9+p.ph))*0.004,ZA-p.line+p.side);dummy.rotation.y=p.dir>0?0:Math.PI;}
    else{dummy.position.set(X0+p.line+p.side,Math.abs(Math.sin(t*9+p.ph))*0.004,ZA-q);dummy.rotation.y=p.dir>0?Math.PI/2:-Math.PI/2;}
    dummy.updateMatrix();bodies.setMatrixAt(i,dummy.matrix);faces.setMatrixAt(i,dummy.matrix);}
  bodies.instanceMatrix.needsUpdate=faces.instanceMatrix.needsUpdate=true;
}
// Static street furniture and the blocks without a campaign
(function(){
  var used={},trees=[],lamps=[],fill=[],lawns=[],sig=[],i,j,c,cx,cz,e=CP/2-RW-SW*0.5,n,a,b;
  D.forEach(function(d){used[(d.y-START)+','+d.s]=1;});
  function low(x,z,h){fill.push([x,z,0.42+0.34*lr(),0.42+0.34*lr(),h]);}
  for(i=-1;i<=YEARS;i++)for(j=0;j<=SLOTS+1;j++){cx=i*CP;cz=-j*CP;
    for(c=0;c<4;c++){lamps.push([cx+(c&1?e:-e),cz+(c&2?e:-e)]);
      for(n=-1;n<2;n+=2){a=n*(0.45+0.5*lr());trees.push(c<2?[cx+(c?e:-e),cz+a]:[cx+a,cz+(c===2?e:-e)]);}}
    if(used[i+','+j]){for(c=0;c<4;c++)if(lr()<0.4)low(cx+(c&1?0.93:-0.93),cz+(c&2?0.93:-0.93),0.1+0.2*lr());}
    else if(lr()<0.42){lawns.push([cx,cz]);for(n=0;n<9;n++)trees.push([cx+(lr()-0.5)*2.1,cz+(lr()-0.5)*2.1]);}   // a park
    else for(a=-1;a<2;a++)for(b=-1;b<2;b++)if(lr()<0.72)low(cx+a*0.86,cz+b*0.86,0.1+0.28*lr());                 // background low-rises
  }
  for(i=1;i<NX;i++)for(j=1;j<NZ;j++){sig.push([X0+i*CP+RW+0.03,ZA-j*CP+RW+0.03],[X0+i*CP-RW-0.03,ZA-j*CP-RW-0.03]);}
  function place(mesh,list,fn){list.forEach(function(s,k){dummy.position.set(s[0],0,s[1]);dummy.rotation.y=0;dummy.scale.set(1,1,1);if(fn)fn(s,k);dummy.updateMatrix();mesh.setMatrixAt(k,dummy.matrix);});}
  var trunks=fleet(trees.length,new THREE.CylinderGeometry(0.006,0.008,0.05,3).translate(0,0.025,0),new THREE.MeshLambertMaterial({color:0x4a3524}));
  var leaves=fleet(trees.length,new THREE.OctahedronGeometry(0.042,0).translate(0,0.078,0),new THREE.MeshLambertMaterial({color:0x2f7048,flatShading:true}));
  var sizes=trees.map(function(){return 0.7+0.8*lr();});
  [trunks,leaves].forEach(function(m){place(m,trees,function(s,k){dummy.rotation.y=k;dummy.scale.setScalar(sizes[k]);});});
  place(fleet(lamps.length,new THREE.CylinderGeometry(0.004,0.004,0.13,3).translate(0,0.065,0),STEEL),lamps);
  place(fleet(lamps.length,new THREE.OctahedronGeometry(0.014,0).translate(0,0.135,0),new THREE.MeshBasicMaterial({color:0xffe2a0})),lamps);
  place(fleet(lawns.length,new THREE.BoxGeometry(2.3,0.02,2.3).translate(0,0.01,0),new THREE.MeshLambertMaterial({color:0x1f4a33})),lawns);
  place(fleet(sig.length,new THREE.CylinderGeometry(0.005,0.005,0.17,3).translate(0,0.085,0),STEEL),sig);
  place(fleet(sig.length,new THREE.OctahedronGeometry(0.015,0).translate(0.018,0.16,0),sigEW),sig);
  place(fleet(sig.length,new THREE.OctahedronGeometry(0.015,0).translate(0,0.16,0.018),sigNS),sig);
  // Background low-rises: plain, dark, no plate and no hover card, so they cannot be mistaken for a campaign
  var wt=canvasTexture(96,48,function(g){g.fillStyle='#9aa2ad';g.fillRect(0,0,96,48);var r2=rng(77),x,y;
    for(y=0;y<3;y++)for(x=0;x<6;x++){g.fillStyle=r2()<0.18?'#d9c48f':'#2a313c';g.fillRect(x*16+4,y*16+4,8,9);}});
  var side=new THREE.MeshLambertMaterial({map:wt}),roofM=new THREE.MeshLambertMaterial({color:0x2a2f37});
  var lows=fleet(fill.length,new THREE.BoxGeometry(1,1,1).translate(0,0.5,0),[side,side,roofM,roofM,side,side]);
  var TONE=[0x6d7480,0x7d7468,0x5d6672,0x86796a,0x70787f];
  place(lows,fill,function(s,k){dummy.scale.set(s[2],s[4],s[3]);lows.setColorAt(k,tmpC.set(TONE[k%TONE.length]));});
  dummy.scale.set(1,1,1);
})();
var STILL=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches,clock=new THREE.Clock(),simT=0;
var frameNo=0,lifeEvery=1;
function animate(){var dt=Math.min(0.05,clock.getDelta());simT+=dt;frameNo++;traffic(dt,simT);if(frameNo%(2*lifeEvery)===0)walk(simT);}
(function(){for(var i=0;i<200;i++){simT+=0.05;traffic(0.05,simT);}walk(simT);})();   // start with traffic already flowing

// ---------- catalog: every building on one sheet, so each design can be checked ----------
var catBuilt=false;
function flyTo(ix){var m=builds[ix],H=D[ix].h*HS,s=Math.max(H,1.2);controls.target.set(m.position.x,H*0.5,m.position.z);
  camera.position.set(m.position.x+s*0.7,H*0.5+s*0.25,m.position.z+s*1.6);controls.update();}
function openCatalog(){
  var cat=document.getElementById('cat');cat.style.display='block';
  if(catBuilt)return;catBuilt=true;
  var W=180,Hh=260,R=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
  R.setPixelRatio(1);R.setSize(W,Hh,false);R.outputEncoding=THREE.sRGBEncoding;R.setClearColor(0x0d131c,1);
  var sc=new THREE.Scene(),cam=new THREE.PerspectiveCamera(26,W/Hh,0.05,100),sun2=new THREE.DirectionalLight(0xffffff,1.5),jobs=[];
  sc.add(new THREE.HemisphereLight(0xc9dcff,0x1a2233,1.25));sc.add(new THREE.AmbientLight(0xffffff,0.5));sun2.position.set(-30,45,40);sc.add(sun2);
  var body=document.getElementById('catbody'),done=0;
  Array.prototype.slice.call(document.getElementById('org').options,1).forEach(function(o){
    var h=document.createElement('h3');h.textContent=o.textContent;body.appendChild(h);
    var grid=document.createElement('div');grid.className='catgrid';body.appendChild(grid);
    D.map(function(d,ix){return ix;}).filter(function(ix){return D[ix].f===o.value;}).sort(function(a,b){return D[a].y-D[b].y;}).forEach(function(ix){
      var d=D[ix],f=document.createElement('figure'),img=document.createElement('img'),cap=document.createElement('figcaption');
      img.width=W;img.height=Hh;img.alt=d.y+' '+d.n;f.style.borderBottomColor=COLORS[d.g];
      cap.innerHTML='<b>'+d.y+'</b> '+d.n+'<br>OPS '+d.o+' · '+LABELS[d.g]+'<br><i>'+d.bn+'</i>';
      f.appendChild(img);f.appendChild(cap);grid.appendChild(f);
      f.addEventListener('click',function(){cat.style.display='none';if(state.view!=='city')set('view','city');flyTo(ix);});
      jobs.push([ix,img]);});
  });
  (function step(){
    for(var n=0;n<8&&jobs.length;n++){var j=jobs.shift(),H=D[j[0]].h*HS,s=Math.max(H,1.1),m=new THREE.Mesh(builds[j[0]].geometry,builds[j[0]].userData.mat);
      sc.add(m);cam.position.set(s*1.05,H*0.5+s*0.5,s*2.2);cam.lookAt(0,H*0.47,0);R.render(sc,cam);j[1].src=R.domElement.toDataURL('image/jpeg',0.88);sc.remove(m);done++;}
    document.getElementById('catnote').textContent=jobs.length?'Drawing '+done+' of '+D.length+'…':D.length+' buildings, one per campaign, grouped by organization and in season order. Each picture is zoomed to fit its building, so sizes here do not compare. Click one to fly to it in the city.';
    if(jobs.length)requestAnimationFrame(step);else R.dispose();
  })();
}
document.getElementById('catopen').addEventListener('click',openCatalog);
document.getElementById('catclose').addEventListener('click',function(){document.getElementById('cat').style.display='none';});
if(/[?&]catalog/.test(location.search))openCatalog();

// ---------- filters ----------
var state;
function defaults(){return {view:state?state.view:(/[?&]view=bars/.test(location.search)?'bars':'city'),org:'',season:'',minG:1,streak:'any',others:'fade'};}
function active(){return state.view==='city'?builds:bars;}
function apply(){
  var shown=0,city=state.view==='city',on=active(),off=city?bars:builds;pick=[];
  ground.material=city?STREETS:PLAIN;life.visible=city;
  document.getElementById('keynote').textContent=city?'City view: every building is modelled on a different real tower. The key colour is the plate under each building and the edge of the hover card.':'';scene.fog.density=city?0.0042:0.0022;
  if(PITCH!==(city?CP:BP)||!apply.ready){apply.ready=1;setPitch(city?CP:BP);homeView();}
  D.forEach(function(d,ix){
    var pass=(!state.org||d.f===state.org)&&(!state.season||d.y===+state.season)&&d.G>=state.minG&&(state.streak==='any'||d.L);
    var o=on[ix];
    if(pass){shown++;pick.push(o);}
    off[ix].visible=false;o.visible=pass||state.others!=='hide';o.material=pass?o.userData.mat:GHOST;
  });
  document.getElementById('count').textContent='Showing '+shown+' of '+D.length+' campaigns';
  hide();
}
function sync(){
  document.querySelectorAll('.grp[data-key]').forEach(function(grp){grp.querySelectorAll('button').forEach(function(b){
    b.classList.toggle('on',String(state[grp.dataset.key])===b.dataset.v);});});
  document.getElementById('org').value=state.org;document.getElementById('season').value=state.season;
  document.getElementById('ming').value=state.minG;document.getElementById('gval').textContent=state.minG;
}
function set(k,v){state[k]=v;sync();apply();}
document.querySelectorAll('.grp[data-key] button').forEach(function(b){b.addEventListener('click',function(){set(b.parentNode.dataset.key,b.dataset.v);});});
document.getElementById('org').addEventListener('change',function(e){set('org',e.target.value);});
document.getElementById('season').addEventListener('change',function(e){set('season',e.target.value);});
document.getElementById('ming').addEventListener('input',function(e){set('minG',+e.target.value);});
document.getElementById('reset').addEventListener('click',function(){state=defaults();sync();apply();});
document.getElementById('view').addEventListener('click',homeView);
document.getElementById('whole').addEventListener('click',wholeField);

// ---------- hover card ----------
var card=document.getElementById('card'),cur=-1,hideTimer=null,mx=0,my=0,moved=false,dragging=false;
var ray=new THREE.Raycaster(),ndc=new THREE.Vector2(),outline=new THREE.Box3Helper(new THREE.Box3(),0xffffff);
outline.visible=false;scene.add(outline);
function place(){
  var w=card.offsetWidth,h=card.offsetHeight,x=mx+18,y=my+18;
  if(x+w>window.innerWidth-8)x=mx-w-18;if(y+h>window.innerHeight-8)y=my-h-18;
  card.style.transform='translate('+Math.max(8,x)+'px,'+Math.max(8,y)+'px)';
}
function hide(){cur=-1;card.style.display='none';outline.visible=false;}
function probe(){
  var rect=renderer.domElement.getBoundingClientRect();
  ndc.set((mx-rect.left)/rect.width*2-1,-((my-rect.top)/rect.height)*2+1);
  ray.setFromCamera(ndc,camera);
  var hit=ray.intersectObjects(pick,false)[0],ix=hit?hit.object.userData.ix:-1;
  if(ix<0){if(cur>=0&&!hideTimer)hideTimer=setTimeout(function(){hideTimer=null;hide();},160);return;}
  clearTimeout(hideTimer);hideTimer=null;
  if(ix!==cur){cur=ix;card.innerHTML=D[ix].t+(state.view==='city'?'<div style="margin-top:6px;color:#8b949e">Modelled on: '+D[ix].bn+'</div>':'');card.style.borderLeftColor=COLORS[D[ix].g];card.style.display='block';
    outline.box.setFromObject(active()[ix]);outline.visible=true;}
  place();
}
renderer.domElement.addEventListener('pointermove',function(e){mx=e.clientX;my=e.clientY;moved=true;});
renderer.domElement.addEventListener('pointerdown',function(){dragging=true;hide();});
window.addEventListener('pointerup',function(){dragging=false;});
renderer.domElement.addEventListener('pointerleave',function(){clearTimeout(hideTimer);hideTimer=null;hide();});

function resize(){var w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}
window.addEventListener('resize',resize);
state=defaults();sync();apply();resize();
// Deep link: ?look=1993-TOR opens close to that campaign's building
(function(){var q=/[?&]look=(\d{4})-(\w+)/.exec(location.search);if(!q)return;
  var ix=D.findIndex(function(d){return d.y===+q[1]&&d.f===q[2];});if(ix>=0&&state.view==='city')flyTo(ix);})();
// If frames run long, render at a lower resolution so movement stays smooth
var lastT=performance.now(),slow=0,fast=0;
function pace(){var now=performance.now(),ms=now-lastT;lastT=now;if(ms>250)return;
  if(ms>24){slow++;fast=0;}else{fast++;if(fast>30)slow=0;}
  if(slow>40&&DPR>0.75){DPR=Math.max(0.75,DPR-0.25);renderer.setPixelRatio(DPR);resize();slow=0;if(DPR<=1)lifeEvery=2;}}
(function loop(){requestAnimationFrame(loop);pace();controls.update();if(life.visible&&!STILL&&document.getElementById('cat').style.display!=='block')animate();else clock.getDelta();if(moved&&!dragging){moved=false;probe();}renderer.render(scene,camera);})();
window.city={scene:scene,camera:camera,controls:controls,builds:builds,bars:bars,D:D,set:set,state:function(){return state;},renderer:renderer,probe:probe};
})();
</script></body></html>
"""


def main():
    df = pd.read_csv(C.CAMPAIGNS_CSV)
    n_all, n_qual = len(df), int(df["qualified"].sum())
    # Slot 1 = best OPS in that year's field (front row), worst at the back
    df["slot"] = df.groupby("year")["OPS"].rank(ascending=False, method="first").astype(int)

    # Drawn height: differences from the median campaign are multiplied by CONTRAST.
    # The transform is linear, so the ruler is still labelled in true OPS.
    median = df["OPS"].median()

    def to_height(ops):
        return median + CONTRAST * (ops - median)

    best = df[df["qualified"]].sort_values("OPS", ascending=False).head(len(BUILDINGS))
    landmark = {(int(r.year), r.franch_id): LANDMARK_ORDER[n] for n, r in enumerate(best.itertuples())}
    # Every other campaign is modelled on its own real tower from real_towers.py: the list runs roughly from
    # the tallest and best known down, and is handed out in order of OPS.
    towers = real_towers.load(len(PALETTE))
    rest = df[~df.index.isin(best.index)].sort_values("OPS", ascending=False)
    if len(towers) < len(rest):
        raise ValueError(f"real_towers.py lists {len(towers)} towers; {len(rest)} are needed")
    model = {(int(r.year), r.franch_id): towers[n] for n, r in enumerate(rest.itertuples())}
    records = []
    for r in df.itertuples():
        key = (int(r.year), r.franch_id)
        if key in landmark:
            bn, b = f"{BUILDINGS[landmark[key]]}, {LANDMARK_CITIES[landmark[key]]}", None
        else:
            bn, b = model[key]
        records.append(dict(y=int(r.year), s=int(r.slot), g=LEVEL_INDEX[r.result], G=int(r.G), f=r.franch_id, n=r.team_name, o=fmt(r.OPS),
                            L=int(bool(r.in_long_streak)), h=round(max(MIN_HEIGHT, to_height(r.OPS)), 4),
                            k=landmark.get(key, -1), bn=bn, b=b, t=hover(r, n_all, n_qual)))
    ticks = [[fmt(v), round(to_height(v), 4)] for v in (0.3, 0.5, 0.7, 0.9) if to_height(v) > 0.03]

    latest = df.sort_values("year").groupby("franch_id").tail(1).set_index("franch_id")["team_name"]
    counts = df.groupby("franch_id").size()
    orgs = sorted(((latest[f], f, int(counts[f])) for f in latest.index))
    org_options = "".join(f'<option value="{f}">{name} ({n})</option>' for name, f, n in orgs)
    season_options = "".join(f'<option value="{y}">{y} ({n} teams)</option>'
                             for y, n in sorted(df.groupby("year").size().items(), reverse=True))
    by_result = df.groupby("result").size()
    key = "".join(f'<li><i style="background:{color}"></i>{label}<b>{int(by_result.get(code, 0))}</b></li>'
                  for code, label, color in reversed(LEVELS))

    def safe(js):  # keep bundled scripts from closing their own <script> tag
        return js.replace("</script", "<\\/script")

    fill = {
        "__BG__": BG, "__PANEL__": PANEL, "__MUTED__": MUTED, "__N__": str(n_all), "__STREAK__": str(C.LONG_STREAK),
        "__KEY__": key, "__ORG_OPTIONS__": org_options, "__SEASON_OPTIONS__": season_options,
        "__MAX_G__": str(int(df["G"].max())), "__HS__": str(HEIGHT_SCALE), "__FOOT__": str(FOOT), "__PITCH__": str(PITCH), "__CITY_PITCH__": str(CITY_PITCH), "__RW__": str(ROAD_HALF), "__SW__": str(SIDEWALK),
        "__LABELS__": json.dumps([label for _, label, _ in LEVELS]),
        "__STOREY__": str(STOREY), "__STYLES__": str(STYLES), "__LOW__": str(LOW_RISE),
        "__NAMES__": json.dumps(BUILDINGS), "__TINTS__": json.dumps(TINTS + PALETTE), "__NAMELIST__": ", ".join(BUILDINGS),
        "__START__": str(C.START_YEAR), "__END__": str(C.END_YEAR),
        "__COLORS__": json.dumps([color for _, _, color in LEVELS]), "__TICKS__": json.dumps(ticks),
        "__DATA__": json.dumps(records, separators=(",", ":")).replace("</", "<\\/"),
        "__THREE__": safe((VENDOR / "three-0.147.0.min.js").read_text(encoding="utf-8")),
        "__ORBIT__": safe((VENDOR / "OrbitControls-0.147.0.js").read_text(encoding="utf-8")),
    }
    html = PAGE
    for token, value in fill.items():
        html = html.replace(token, value)

    C.OUT.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(C.ROOT)} ({OUT_FILE.stat().st_size / 1e6:.1f} MB): {n_all} buildings, "
          f"{len(BUILDINGS)} detailed landmarks, {n_all - len(BUILDINGS)} other real towers")
    for n, r in enumerate(best.itertuples()):
        print(f"  {BUILDINGS[LANDMARK_ORDER[n]]}: {int(r.year)} {r.team_name} ({fmt(r.OPS)})")

if __name__ == "__main__":
    main()
