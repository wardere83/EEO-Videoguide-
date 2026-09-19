"""Render a silent, continuous CCCCO-branded EEO IBP motion story."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, math, os, subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT, FONTS = ROOT / "public/media", ROOT / "public/fonts"
FFMPEG = os.environ.get("FFMPEG") or str(ROOT / "node_modules/ffmpeg-static/ffmpeg")
W, H, FPS = 1920, 800, 24
NAVY, DEEP, INK = (0, 47, 109), (0, 39, 85), (0, 25, 58)
BLUE, LIGHT, GOLD = (0, 102, 186), (64, 180, 229), (255, 182, 0)
MIST, WHITE = (207, 224, 238), (255, 255, 255)
regular = lambda size: ImageFont.truetype(str(FONTS / "font-2.ttf"), size)
serif = lambda size: ImageFont.truetype(str(FONTS / "font-0.ttf"), size)
bold = lambda size: ImageFont.truetype(str(FONTS / "font-4.ttf"), size)
scenes = json.loads((ROOT / "src/film.json").read_text())
TOTAL = sum(scene["duration"] for scene in scenes)


def clamp(v): return max(0, min(1, v))
def ease(v): return 1 - (1 - clamp(v)) ** 3
def alpha(c, o): return (*c, int(255 * clamp(o)))
def reveal(t, delay=.15, speed=.9): return ease((t-delay)/speed)
def fade(t, duration): return min(ease(t/.55), ease((duration-t)/.55))


def wrap(draw, value, font, width):
    lines, line = [], ""
    for word in value.split():
        trial = f"{line} {word}".strip()
        if line and draw.textlength(trial, font=font) > width:
            lines.append(line); line = word
        else: line = trial
    if line: lines.append(line)
    return lines


def text(draw, xy, value, font, color, opacity=1, anchor=None):
    draw.text(xy, value, font=font, fill=alpha(color, opacity), anchor=anchor)


def curve(control, steps=80):
    p0, p1, p2, p3 = control; points = []
    for i in range(steps+1):
        t, u = i/steps, 1-i/steps
        points.append((p0[0]*u**3+3*p1[0]*u*u*t+3*p2[0]*u*t*t+p3[0]*t**3,
                       p0[1]*u**3+3*p1[1]*u*u*t+3*p2[1]*u*t*t+p3[1]*t**3))
    return points


def make_base():
    image = Image.new("RGBA", (W, H), INK+(255,)); draw = ImageDraw.Draw(image)
    for y in range(H):
        r = y/H; c = tuple(int(DEEP[i]*(1-r)+INK[i]*r) for i in range(3))
        draw.line((0, y, W, y), fill=c+(255,))
    return image


BASE = make_base()
PATHS = [
    curve([(830, 650), (1110, 190), (1510, 760), (2040, 180)]),
    curve([(760, 190), (1120, 690), (1540, -60), (2070, 540)]),
    curve([(900, 430), (1260, 90), (1600, 690), (2020, 350)]),
]


def background(global_t):
    image = BASE.copy(); draw = ImageDraw.Draw(image, "RGBA")
    for j, points in enumerate(PATHS):
        draw.line(points, fill=alpha(LIGHT if j != 1 else BLUE, .12), width=2)
        for i in range(4):
            phase = (global_t*(.035+j*.006)+i*.25+j*.11) % 1
            x, y = points[int(phase*(len(points)-1))]; radius = 5 if i == 0 else 3
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=alpha(LIGHT, .44))
    for i in range(18):
        x = (i*241+global_t*(4+i%3)) % (W+120)-60
        y = 78+(i*113)%650+math.sin(global_t*.18+i)*18
        draw.ellipse((x-2, y-2, x+2, y+2), fill=alpha(MIST, .18))
    text(draw, (82, 58), "EQUAL EMPLOYMENT OPPORTUNITY", regular(15), MIST, .8)
    text(draw, (1838, 58), "FUNDING · PRACTICE · IMPACT", bold(12), MIST, .48, "ra")
    return image


def chapter(draw, kicker, title, detail, local, width=760, size=76):
    p = reveal(local); offset = int((1-p)*18)
    text(draw, (82, 190+offset), kicker.upper(), bold(16), LIGHT, p)
    y, face = 244+offset, regular(size)
    lines = wrap(draw, title, face, width)
    for index, line in enumerate(lines):
        text(draw, (82, y), line, face, LIGHT if index == len(lines)-1 else WHITE, p)
        y += int(size*.98)
    y += 34
    for line in wrap(draw, detail, regular(22), width):
        text(draw, (82, y), line, regular(22), MIST, p*.92); y += 31


def metric(draw, amount, kicker, detail, local):
    p = reveal(local); offset = int((1-p)*16)
    text(draw, (82, 214+offset), kicker.upper(), bold(16), LIGHT, p)
    text(draw, (82, 274+offset), amount, regular(126), WHITE, p)
    text(draw, (82, 430+offset), detail, regular(27), LIGHT, p)


def ring(draw, center, radius, start, end, color, opacity, width=4):
    x, y = center
    draw.arc((x-radius, y-radius, x+radius, y+radius), start=start, end=end,
             fill=alpha(color, opacity), width=width)


def dot_sphere(draw, center, radius, global_t, opacity):
    """A restrained rotating identity sphere inspired by the XpressTend film."""
    cx, cy = center
    dots = []
    yaw = global_t*.11
    for latitude in range(-72, 73, 12):
        phi = math.radians(latitude)
        for longitude in range(0, 360, 12):
            theta = math.radians(longitude)+yaw
            x3 = math.cos(phi)*math.cos(theta)
            y3 = math.sin(phi)
            z3 = math.cos(phi)*math.sin(theta)
            x, y = cx+x3*radius, cy-y3*radius
            dots.append((z3, x, y))
    for depth, x, y in sorted(dots):
        visibility = .12+.76*((depth+1)/2)
        size = 1.4+1.8*((depth+1)/2)
        draw.ellipse((x-size, y-size, x+size, y+size), fill=alpha(LIGHT, opacity*visibility))
    for index, tilt in enumerate((-24, 8, 31)):
        box = (cx-radius*1.18, cy-radius*.72, cx+radius*1.18, cy+radius*.72)
        draw.arc(box, start=185+tilt+global_t*(3+index), end=510+tilt+global_t*(3+index), fill=alpha(MIST, opacity*.12), width=2)


def finish(image, local, duration):
    opacity = fade(local, duration)
    if opacity < 1: image.alpha_composite(Image.new("RGBA", (W, H), INK+(int(255*(1-opacity)),)))
    return image.convert("RGB")


def opener(t, duration, gt, _):
    image = background(gt); draw = ImageDraw.Draw(image, "RGBA")
    chapter(draw, "A statewide system for progress", "Ideas become infrastructure.",
            "Investment · practice · evidence · lasting opportunity", t, 780, 82)
    p, center = reveal(t, .45, 1.25), (1460, 400)
    dot_sphere(draw, center, 260, gt, p)
    for index in range(5):
        angle = -1.8+index*.82+gt*.045
        x, y = center[0]+math.cos(angle)*330, center[1]+math.sin(angle)*210
        draw.ellipse((x-5,y-5,x+5,y+5), fill=alpha(LIGHT,p*(.5+index*.08)))
    return finish(image, t, duration)


def foundation(t, duration, gt, _):
    image = background(gt); draw = ImageDraw.Draw(image, "RGBA")
    metric(draw, "$20M", "Statewide foundation · 2021", "$15.5M apportioned systemwide", t)
    p, center = reveal(t, .35, 1.25), (1460, 395)
    ring(draw, center, 248, -90, -90+360*.775*p, LIGHT, p, 18)
    ring(draw, center, 284, 16+gt*4, 235+gt*4, BLUE, p*.38, 3)
    ring(draw, center, 318, 198-gt*3, 410-gt*3, MIST, p*.18, 2)
    text(draw, (center[0], center[1]-22), "$15.5M", regular(76), WHITE, p, "mm")
    text(draw, (center[0], center[1]+52), "APPORTIONED TO ELIGIBLE DISTRICTS", bold(14), MIST, p, "mm")
    text(draw, (center[0], 715), "77.5% OF THE STATEWIDE FOUNDATION", bold(13), LIGHT, p, "mm")
    return finish(image, t, duration)


def first_cycle(t, duration, gt, _):
    image = background(gt); draw = ImageDraw.Draw(image, "RGBA")
    metric(draw, "$5.65M", "First competitive cycle · 2023–25", "21 district award selections", t)
    p, center = reveal(t, .35, 1.1), (1460, 400)
    for i in range(21):
        a = -math.pi/2+i*2*math.pi/21+math.sin(gt*.18)*.06; radius = 150+(i%3)*62
        x, y = center[0]+math.cos(a)*radius, center[1]+math.sin(a)*radius
        q = ease((p-i*.018)/.72); draw.line((*center, x, y), fill=alpha(LIGHT, q*.17), width=2)
        size = 11 if i%3 == 0 else 8
        draw.ellipse((x-size, y-size, x+size, y+size), fill=alpha(WHITE if i%4 == 0 else LIGHT, q))
    ring(draw, center, 102, -90+gt*7, 226+gt*7, BLUE, p*.72, 5)
    text(draw, center, "21", regular(72), WHITE, p, "mm")
    text(draw, (center[0], center[1]+60), "DISTRICTS", bold(13), MIST, p, "mm")
    return finish(image, t, duration)


def current_cycle(t, duration, gt, _):
    image = background(gt); draw = ImageDraw.Draw(image, "RGBA")
    metric(draw, "$1.4M", "Current cycle · 2026–28", "11 district awards", t)
    p, awards, baseline = reveal(t, .35, 1.05), [100,100,100,150,150,150,100,150,150,150,100], 590
    for i, amount in enumerate(awards):
        x, q = 1080+i*71, ease((p-i*.028)/.72); height = (205 if amount == 100 else 305)*q
        draw.line((x, baseline, x, baseline-height), fill=alpha(BLUE if amount == 100 else LIGHT, q), width=7)
        glow = 12+3*math.sin(gt*2+i)
        draw.ellipse((x-glow, baseline-height-glow, x+glow, baseline-height+glow), fill=alpha(WHITE if i in (1,6,10) else LIGHT, q*.94))
        text(draw, (x, baseline+34), f"{i+1:02d}", bold(12), MIST, q, "mm")
        text(draw, (x, baseline-height-35), f"${amount}K", bold(11), WHITE, q, "mm")
    text(draw, (1460, 700), "FIVE $100K AWARDS  ·  SIX $150K AWARDS", bold(13), MIST, p, "mm")
    return finish(image, t, duration)


def combined(t, duration, gt, _):
    image = background(gt); draw = ImageDraw.Draw(image, "RGBA")
    metric(draw, "$7.05M", "Competitive awards since launch", "32 award selections · two cycles", t)
    p, target = reveal(t, .35, 1.1), (1605, 400)
    flows = [((1010,235),(1220,200),(1390,350),target,"$5.65M","2023–25"),
             ((1010,570),(1210,610),(1400,450),target,"$1.4M","2026–28")]
    for i, (*control, amount, year) in enumerate(flows):
        points = curve(control); draw.line(points[:max(2, int(len(points)*p))], fill=alpha(LIGHT if i else BLUE, p*.8), width=8 if i else 14)
        text(draw, (control[0][0], control[0][1]-34), amount, regular(43), WHITE, p)
        text(draw, (control[0][0], control[0][1]+28), year, bold(13), MIST, p)
        for dot in range(5):
            x, y = points[int(((gt*.16+dot*.2+i*.08)%1)*(len(points)-1))]
            draw.ellipse((x-5,y-5,x+5,y+5), fill=alpha(LIGHT,p))
    draw.ellipse((1499,294,1711,506), fill=alpha(DEEP,p), outline=alpha(LIGHT,p), width=4)
    text(draw, (1605,385), "32", regular(64), WHITE, p, "mm")
    text(draw, (1605,443), "AWARD SELECTIONS", bold(12), MIST, p, "mm")
    return finish(image, t, duration)


def districts(t, duration, gt, _):
    image = background(gt); draw = ImageDraw.Draw(image, "RGBA")
    chapter(draw, "Eleven local signals", "Local projects. Shared learning.",
            "Seven Tier 1 districts · Four Tier 2 LIFT districts", t, 700, 70)
    p, center, tier2 = reveal(t,.35,1.1), (1480,400), {1,2,3,10}; positions=[]
    for i in range(11):
        a=-math.pi/2+i*2*math.pi/11; radius=270 if i%2 else 230
        positions.append((center[0]+math.cos(a)*radius, center[1]+math.sin(a)*radius))
    ordered=sorted(tier2)
    for i,(x,y) in enumerate(positions):
        q=ease((p-i*.025)/.75); draw.line((*center,x,y), fill=alpha(LIGHT,q*.25), width=2)
        if i in tier2:
            nx,ny=positions[ordered[(ordered.index(i)+1)%4]]; draw.line((x,y,nx,ny), fill=alpha(WHITE,q*.28), width=2)
        size=21 if i in tier2 else 15
        draw.ellipse((x-size,y-size,x+size,y+size), fill=alpha(WHITE if i in tier2 else LIGHT,q))
        text(draw,(x,y),str(i+1),bold(11),DEEP,q,"mm")
    draw.ellipse((1391,311,1569,489), fill=alpha(DEEP,p), outline=alpha(LIGHT,p), width=4)
    text(draw,(1480,385),"$1.4M",regular(52),WHITE,p,"mm"); text(draw,(1480,436),"11 DISTRICTS",bold(12),MIST,p,"mm")
    return finish(image,t,duration)


def sustainable(t, duration, gt, _):
    image=background(gt); draw=ImageDraw.Draw(image,"RGBA")
    chapter(draw,"Sustainable impact model","Investment that compounds.",
            "Projects become tested practices. Practices build shared capacity.",t,720,70)
    p,center=reveal(t,.35,1),(1480,400); labels=[("INVEST",-90),("IMPLEMENT",0),("LEARN",90),("SUSTAIN",180)]
    ring(draw,center,260,-90,-90+360*p,LIGHT,p*.45,4)
    for i,(label,degrees) in enumerate(labels):
        a=math.radians(degrees); x,y=center[0]+math.cos(a)*260,center[1]+math.sin(a)*260; q=ease((p-i*.06)/.76)
        draw.ellipse((x-61,y-61,x+61,y+61),fill=alpha(DEEP,q),outline=alpha(WHITE if label=="SUSTAIN" else LIGHT,q),width=4 if label=="SUSTAIN" else 3)
        text(draw,(x,y),label,bold(14),WHITE,q,"mm")
    for i in range(4):
        a=-math.pi/2+((gt*.11+i*.25)%1)*2*math.pi; x,y=center[0]+math.cos(a)*260,center[1]+math.sin(a)*260
        draw.ellipse((x-7,y-7,x+7,y+7),fill=alpha(LIGHT,p))
    return finish(image,t,duration)


def finale(t, duration, gt, _):
    image=background(gt); draw=ImageDraw.Draw(image,"RGBA"); opacity=fade(t,duration); p=ease(t/2)
    starts=[(-240,300),(960,-180),(2180,500)]; finals=[760,960,1160]
    for i,letter in enumerate("IBP"):
        q=ease((p-i*.08)/.84); x=starts[i][0]+(finals[i]-starts[i][0])*q; y=starts[i][1]+(335-starts[i][1])*q
        text(draw,(x,y),letter,regular(178),WHITE if i == 0 else LIGHT,opacity*q,"mm")
    line=ease((t-1.35)/1); draw.rounded_rectangle((655,475,655+610*line,479),radius=2,fill=alpha(LIGHT,opacity*.72))
    text(draw,(960,540),"GRANT INITIATIVE",regular(29),WHITE,opacity*ease((t-1.7)/.9),"mm")
    text(draw,(960,598),"IDEAS · PRACTICE · EVIDENCE · SUSTAINABLE IMPACT",bold(13),MIST,opacity*ease((t-2.4)/.9),"mm")
    return finish(image,t,duration)


RENDERERS=[opener,foundation,first_cycle,current_cycle,combined,districts,sustainable,finale]
def timestamp(s): return f"{int(s//3600):02d}:{int(s//60%60):02d}:{int(s%60):02d}.{int(round((s-int(s))*1000)):03d}"


def main():
    if not Path(FFMPEG).exists(): raise SystemExit(f"ffmpeg not found at {FFMPEG}")
    OUT.mkdir(exist_ok=True); mp4=OUT/"eeo-initiative.mp4"
    command=[FFMPEG,"-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","medium","-crf","15","-pix_fmt","yuv420p","-movflags","+faststart",str(mp4)]
    process=subprocess.Popen(command,stdin=subprocess.PIPE); starts=[]; elapsed=0
    for scene in scenes: starts.append(elapsed); elapsed+=scene["duration"]
    poster=False
    for frame_no in range(int(TOTAL*FPS)):
        current=frame_no/FPS; index=max(i for i,start in enumerate(starts) if start<=current); local=current-starts[index]
        image=RENDERERS[index](local,scenes[index]["duration"],current,index)
        if not poster and current>=3.4: image.save(OUT/"eeo-poster.jpg",quality=97,subsampling=0); poster=True
        process.stdin.write(image.tobytes())
        if frame_no%(FPS*5)==0: print(f"Rendered {frame_no//FPS:02d}s / {TOTAL}s",flush=True)
    process.stdin.close()
    if process.wait()!=0: raise SystemExit("MP4 render failed")
    subprocess.run([FFMPEG,"-hide_banner","-loglevel","error","-y","-i",str(mp4),"-an","-c:v","libvpx-vp9","-crf","26","-b:v","0","-deadline","good","-cpu-used","3",str(OUT/"eeo-initiative.webm")],check=True)
    captions,elapsed=["WEBVTT",""],0
    for scene in scenes:
        end=elapsed+scene["duration"]; captions.extend([f"{timestamp(elapsed)} --> {timestamp(end)}",scene["title"],scene.get("transcript",scene["description"]),""]); elapsed=end
    (OUT/"eeo-initiative.en.vtt").write_text("\n".join(captions))
    print(f"Complete: {TOTAL}s silent 1920x800 explainer",flush=True)


if __name__=="__main__": main()
