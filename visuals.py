"""Animated, geometric TLC illustration with a prediction-linked spot."""
import html
import math

def tlc_scene(rf=None, animate=True):
    """Return an isometric TLC plate; distances follow the displayed Rf exactly."""
    demo = rf is None
    value = 0.56 if demo else float(rf)
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError('Rf must be finite and between 0 and 1.')
    # Plate coordinates: baseline 250 px, final solvent front 40 px.
    distance = 210 * value
    top = 250 - distance
    label = 'ILLUSTRATION' if demo else 'PREDICTED POSITION'
    rf_text = 'Rf = d / D' if demo else f'Rf = {value:.4f}'
    motion = 'running' if animate else 'paused'
    return f'''<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{{box-sizing:border-box}}body{{margin:0;font-family:Arial,sans-serif;color:#153b5b;background:transparent}}
.scene{{height:410px;border-radius:26px;background:radial-gradient(ellipse at 50% 15%,#fff 0,#e1f1ff 65%,#cfe6fa 100%);position:relative;overflow:hidden;border:1px solid #cee4f6}}
.orbit{{position:absolute;width:310px;height:310px;border:1px solid #a8d2f0;border-radius:50%;left:50%;top:47%;transform:translate(-50%,-50%) rotateX(60deg)}}
.orbit.two{{width:430px;height:430px;opacity:.4}}
.stage{{position:absolute;left:50%;top:52%;perspective:1000px}}
.plate{{position:absolute;width:190px;height:290px;left:-95px;top:-145px;background:linear-gradient(120deg,#fff,#edf8ff 48%,#dceefb);border:1px solid #8fbbdb;border-radius:9px;transform:rotateX(15deg) rotateY(-24deg) rotateZ(8deg);box-shadow:14px 20px 0 -8px #9bc8e8,24px 35px 40px #3477a733}}
.plate:before{{content:'';position:absolute;inset:0;border-radius:9px;background:repeating-linear-gradient(0deg,transparent 0px,transparent 18px,#a5cbe215 19px)}}
.front{{position:absolute;left:10px;right:10px;height:210px;bottom:40px;background:linear-gradient(to top,#48ace12b,#5eb9ed10);border-top:2px dashed #4b9ed0;transform-origin:bottom;animation:rise 5s ease-in-out infinite;animation-play-state:{motion}}}
.baseline{{position:absolute;left:10px;right:10px;top:250px;border-top:1px dashed #7497ad}}
.spot{{position:absolute;left:76px;top:{top-13:.4f}px;width:26px;height:26px;border-radius:50%;background:radial-gradient(circle,#167ac5 0,#3e9fdfbb 36%,#60b9ee00 72%);animation:migrate 5s ease-in-out infinite;animation-play-state:{motion}}}
.origin{{position:absolute;left:87px;top:247px;width:5px;height:5px;background:#28658e;border-radius:50%}}
.measure{{position:absolute;left:43px;top:{top:.4f}px;height:{distance:.4f}px;border-left:1px solid #2884bf}}
.measure:before,.measure:after{{content:'';position:absolute;width:9px;border-top:1px solid #2884bf;left:-5px}}.measure:before{{top:0}}.measure:after{{bottom:0}}
.d-label{{position:absolute;left:24px;top:{top+distance/2-8:.4f}px;font-size:12px;color:#287fb6}}
.front-label{{position:absolute;left:12px;top:20px;font-size:9px;letter-spacing:.9px;color:#4389b6}}
.base-label{{position:absolute;left:12px;bottom:17px;font-size:9px;letter-spacing:.9px;color:#7595ad}}
.badge{{position:absolute;top:23px;left:24px;letter-spacing:2px;font-size:10px;font-weight:bold;color:#387aaf}}
.rf{{position:absolute;right:22px;bottom:24px;padding:11px 15px;border:1px solid #bad9ef;border-radius:14px;background:#ffffffd9;font-size:17px;font-weight:bold;box-shadow:0 7px 20px #5a94bc14}}
.key{{position:absolute;bottom:26px;left:23px;font-size:10px;color:#4a7697;line-height:1.7}}
.bubble{{position:absolute;border-radius:50%;background:#75b9ed50;width:6px;height:6px;animation:float 7s infinite;animation-play-state:{motion}}}
.b1{{left:14%;bottom:15%}}.b2{{right:12%;bottom:30%;animation-delay:-2s;width:10px;height:10px}}.b3{{left:23%;bottom:35%;animation-delay:-4s;width:4px;height:4px}}
@keyframes rise{{0%,10%{{transform:scaleY(.025)}}65%,90%{{transform:scaleY(1)}}100%{{transform:scaleY(.025)}}}}
@keyframes migrate{{0%,10%{{transform:translateY({distance:.4f}px)}}65%,90%{{transform:translateY(0)}}100%{{transform:translateY({distance:.4f}px)}}}}
@keyframes float{{0%{{transform:translateY(0);opacity:0}}25%{{opacity:1}}100%{{transform:translateY(-170px);opacity:0}}}}
@media(prefers-reduced-motion:reduce){{.front,.spot,.bubble{{animation:none}}}}
</style></head><body><div class="scene" role="img" aria-label="{html.escape('Illustrative TLC development' if demo else f'Predicted TLC spot at Rf {value:.4f}')} . The animation is illustrative, not a kinetic simulation.">
<div class="badge">{label}</div><div class="orbit"></div><div class="orbit two"></div>
<div class="bubble b1"></div><div class="bubble b2"></div><div class="bubble b3"></div>
<div class="stage"><div class="plate"><div class="front"></div><div class="baseline"></div>
<div class="front-label">SOLVENT FRONT · D</div><div class="measure"></div><div class="d-label">d</div><div class="origin"></div><div class="spot"></div><div class="base-label">BASELINE</div></div></div>
<div class="key">d · spot distance<br>D · solvent-front distance</div><div class="rf">{rf_text}</div></div></body></html>'''
