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


def make_base():
    image = Image.new("RGBA", (W, H), INK+(255,)); draw = ImageDraw.Draw(image)
    for y in range(H):
        r = y/H; c = tuple(int(DEEP[i]*(1-r)+INK[i]*r) for i in range(3))
        draw.line((0, y, W, y), fill=c+(255,))
    return image


BASE = make_base()


def background(global_t):
    image = BASE.copy(); draw = ImageDraw.Draw(image, "RGBA")
    # Keep ambient motion inside the visual field so copy always has a quiet canvas.
    for row in range(9):
        for col in range(12):
            x = 1010 + col * 70
            y = 118 + row * 70
            pulse = .5 + .5 * math.sin(global_t * .55 + row * .7 + col * .42)
            radius = 1.4 + pulse * .8
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=alpha(MIST, .035 + pulse * .025))
    text(draw, (82, 58), "EQUAL EMPLOYMENT OPPORTUNITY", regular(15), MIST, .8)
    text(draw, (1838, 58), "FUNDING · PRACTICE · IMPACT", bold(12), MIST, .48, "ra")
    return image


def chapter(draw, kicker, title, detail, local, width=780, size=76):
    p = reveal(local); offset = int((1-p)*18)
    text(draw, (82, 190+offset), kicker.upper(), bold(16), LIGHT, p)
    y, face = 244+offset, regular(size)
    lines = wrap(draw, title, face, width)
    for index, line in enumerate(lines):
        text(draw, (82, y), line, face, LIGHT if index == len(lines)-1 else WHITE, p)
        y += int(size*.98)
    y += 34
    for line in wrap(draw, detail, regular(26), width):
        text(draw, (82, y), line, regular(26), MIST, p*.94); y += 38


def metric(draw, amount, kicker, detail, local, description=""):
    p = reveal(local); offset = int((1-p)*16)
    text(draw, (82, 214+offset), kicker.upper(), bold(16), LIGHT, p)
    text(draw, (82, 274+offset), amount, regular(126), WHITE, p)
    text(draw, (82, 430+offset), detail, regular(30), LIGHT, p)
    y = 500 + offset
    for line in wrap(draw, description, regular(23), 760):
        text(draw, (82, y), line, regular(23), MIST, p*.92); y += 34


def panel(draw, box, opacity=1):
    draw.rounded_rectangle(box, radius=28, fill=alpha(DEEP, opacity*.9), outline=alpha(MIST, opacity*.16), width=2)


def caption(draw, xy, value, opacity=1, anchor=None):
    text(draw, xy, value.upper(), bold(14), MIST, opacity, anchor)


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
    chapter(draw, "CCCCO · EEO INNOVATIVE BEST PRACTICES", "District ideas become statewide progress.",
            "The EEO IBP Grant Initiative funds district-led approaches that advance equitable hiring, retention, and institutional practice.", t, 790, 72)
    p = reveal(t, .45, 1.2)
    panel(draw, (1040, 142, 1818, 674), p)
    caption(draw, (1092, 188), "How the initiative works", p)
    steps = [("01", "INVEST", "Fund district innovation"), ("02", "IMPLEMENT", "Put new practices to work"),
             ("03", "LEARN", "Measure and share results"), ("04", "SUSTAIN", "Build systemwide capacity")]
    for i, (number, label, detail) in enumerate(steps):
        q = ease((p-i*.07)/.75); y = 256+i*92
        draw.rounded_rectangle((1090,y-31,1152,y+31), radius=17, fill=alpha(BLUE,q))
        text(draw,(1121,y),number,bold(14),WHITE,q,"mm")
        text(draw,(1190,y-18),label,bold(18),WHITE,q)
        text(draw,(1190,y+12),detail,regular(18),MIST,q)
        draw.rounded_rectangle((1655,y-4,1748,y+4),radius=4,fill=alpha(LIGHT,q*.18))
        draw.rounded_rectangle((1655,y-4,1655+93*min(1,(gt*.18+i*.2)%1),y+4),radius=4,fill=alpha(LIGHT,q))
    return finish(image, t, duration)


def foundation(t, duration, gt, _):
    image = background(gt); draw = ImageDraw.Draw(image, "RGBA")
    metric(draw, "$20M", "Statewide foundation · 2021", "$15.5M apportioned systemwide", t,
           "AB 132 established a one-time EEO Best Practices Fund. Eligible districts received the statewide foundation in 2021–22.")
    p, center = reveal(t, .35, 1.25), (1460, 395)
    panel(draw, (1040, 122, 1818, 684), p)
    ring(draw, center, 248, -90, -90+360*.775*p, LIGHT, p, 18)
    ring(draw, center, 248, -90+360*.775*p, 270, BLUE, p*.48, 18)
    text(draw, (center[0], center[1]-22), "$15.5M", regular(76), WHITE, p, "mm")
    text(draw, (center[0], center[1]+52), "TO ELIGIBLE DISTRICTS", bold(15), MIST, p, "mm")
    caption(draw, (1460, 638), "77.5% of the statewide fund", p, "mm")
    return finish(image, t, duration)


def first_cycle(t, duration, gt, _):
    image = background(gt); draw = ImageDraw.Draw(image, "RGBA")
    metric(draw, "$5.65M", "First competitive cycle · 2023–25", "21 district award selections", t,
           "Competitive grants expanded local experimentation and created practices that other colleges can study and adapt.")
    p = reveal(t, .35, 1.1)
    panel(draw, (1040, 142, 1818, 674), p)
    caption(draw, (1092, 190), "Twenty-one funded district projects", p)
    for i in range(21):
        row, col = divmod(i, 7); x, y = 1120+col*96, 286+row*106
        q = ease((p-i*.022)/.72); radius = 25+2*math.sin(gt*1.2+i)
        draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=alpha(LIGHT if i%4 else WHITE,q))
        text(draw,(x,y),f"{i+1:02d}",bold(12),DEEP,q,"mm")
    draw.rounded_rectangle((1092,579,1758,591),radius=6,fill=alpha(MIST,p*.14))
    draw.rounded_rectangle((1092,579,1092+666*p,591),radius=6,fill=alpha(LIGHT,p))
    text(draw,(1092,624),"LOCAL INNOVATION",bold(13),MIST,p)
    text(draw,(1758,624),"SHARED PRACTICE",bold(13),MIST,p,"ra")
    return finish(image, t, duration)


def current_cycle(t, duration, gt, _):
    image = background(gt); draw = ImageDraw.Draw(image, "RGBA")
    metric(draw, "$1.4M", "Current cycle · 2026–28", "11 district awards", t,
           "Awards support innovative pre-hiring, post-hiring, and EEO interventions with two levels of district investment.")
    p = reveal(t, .35, 1.05)
    panel(draw, (1040, 142, 1818, 674), p)
    caption(draw,(1092,190),"Award portfolio",p)
    groups=[("AWARD LEVEL","5 AWARDS × $100K","$500K",5,BLUE),("AWARD LEVEL","6 AWARDS × $150K","$900K",6,LIGHT)]
    for row,(name,formula,total,count,color) in enumerate(groups):
        y=292+row*190; q=ease((p-row*.12)/.82)
        text(draw,(1092,y-34),name,bold(18),WHITE,q)
        text(draw,(1092,y),formula,regular(20),MIST,q)
        text(draw,(1748,y-15),total,regular(42),WHITE,q,"ra")
        for i in range(count):
            x=1105+i*83
            draw.rounded_rectangle((x,y+54,x+57,y+82),radius=14,fill=alpha(color,q*(.78+i*.035)))
        draw.rounded_rectangle((1608,y+54,1748,y+82),radius=14,fill=alpha(color,q*.16))
        draw.rounded_rectangle((1608,y+54,1608+140*q,y+82),radius=14,fill=alpha(color,q))
    return finish(image, t, duration)


def combined(t, duration, gt, _):
    image = background(gt); draw = ImageDraw.Draw(image, "RGBA")
    metric(draw, "$7.05M", "Competitive awards since launch", "32 award selections · two cycles", t,
           "This total separates competitive awards from the earlier statewide apportionment, preventing double counting.")
    p = reveal(t, .35, 1.1)
    panel(draw,(1040,142,1818,674),p)
    caption(draw,(1092,190),"Competitive funding history",p)
    bars=[("2023–25","$5.65M",.801,BLUE,"21 selections"),("2026–28","$1.4M",.199,LIGHT,"11 selections")]
    for row,(year,amount,share,color,selections) in enumerate(bars):
        y=290+row*160; q=ease((p-row*.1)/.8)
        text(draw,(1092,y-34),year,bold(16),MIST,q)
        text(draw,(1748,y-34),f"{amount} · {selections}",bold(16),WHITE,q,"ra")
        draw.rounded_rectangle((1092,y,1748,y+54),radius=18,fill=alpha(MIST,q*.12))
        draw.rounded_rectangle((1092,y,1092+656*share*q,y+54),radius=18,fill=alpha(color,q))
    draw.line((1092,574,1748,574),fill=alpha(MIST,p*.18),width=2)
    text(draw,(1092,620),"TOTAL",bold(14),MIST,p)
    text(draw,(1748,620),"$7,051,806",regular(34),WHITE,p,"ra")
    return finish(image, t, duration)


def districts(t, duration, gt, _):
    image = background(gt); draw = ImageDraw.Draw(image, "RGBA")
    chapter(draw, "Current district portfolio", "Local projects. Shared learning.",
            "Eleven districts are testing EEO interventions while building knowledge the broader system can use.", t, 780, 68)
    p = reveal(t,.35,1.1)
    panel(draw,(1040,142,1818,674),p)
    caption(draw,(1092,190),"2026–28 award structure",p)
    tiers=[("TIER 1","7 DISTRICTS","Focused district implementation",7,BLUE),
           ("TIER 2 LIFT","4 DISTRICTS","Deeper collaboration and learning",4,LIGHT)]
    for row,(name,count,detail,total,color) in enumerate(tiers):
        y=292+row*184; q=ease((p-row*.1)/.8)
        text(draw,(1092,y-35),name,bold(18),WHITE,q)
        text(draw,(1748,y-35),count,bold(16),LIGHT,q,"ra")
        text(draw,(1092,y),detail,regular(20),MIST,q)
        for i in range(total):
            x=1106+i*86
            pulse=.86+.14*math.sin(gt*1.3+i*.7)
            draw.ellipse((x-18,y+54-18,x+18,y+54+18),fill=alpha(color,q*pulse))
            text(draw,(x,y+54),f"{i+1:02d}",bold(10),DEEP,q,"mm")
    text(draw,(1429,628),"$1.4M IN MOTION",bold(15),MIST,p,"mm")
    return finish(image,t,duration)


def sustainable(t, duration, gt, _):
    image=background(gt); draw=ImageDraw.Draw(image,"RGBA")
    chapter(draw,"Sustainable impact model","Investment that compounds.",
            "Projects become tested practices. Evidence builds shared capacity. Capacity sustains systemwide EEO progress.",t,780,68)
    p=reveal(t,.35,1)
    panel(draw,(1040,142,1818,674),p)
    caption(draw,(1092,190),"From award to lasting practice",p)
    stages=[("01","INVEST","Resource the idea"),("02","IMPLEMENT","Test in practice"),("03","LEARN","Document evidence"),("04","SUSTAIN","Share what works")]
    for i,(number,label,detail) in enumerate(stages):
        q=ease((p-i*.08)/.76); y=272+i*91
        draw.rounded_rectangle((1092,y-30,1152,y+30),radius=16,fill=alpha(LIGHT if i==3 else BLUE,q))
        text(draw,(1122,y),number,bold(13),WHITE,q,"mm")
        text(draw,(1190,y-17),label,bold(18),WHITE,q)
        text(draw,(1190,y+13),detail,regular(18),MIST,q)
        if i<3:
            draw.rounded_rectangle((1660,y-3,1748,y+3),radius=3,fill=alpha(LIGHT,q*.2))
            draw.rounded_rectangle((1660,y-3,1660+88*((gt*.22+i*.21)%1),y+3),radius=3,fill=alpha(LIGHT,q))
    return finish(image,t,duration)


def finale(t, duration, gt, _):
    image=background(gt); draw=ImageDraw.Draw(image,"RGBA"); opacity=fade(t,duration); p=ease(t/1.7)
    text(draw,(960,272),"EEO",bold(18),LIGHT,opacity*p,"mm")
    text(draw,(960,380),"IBP Grant Initiative",regular(92),WHITE,opacity*p,"mm")
    line=ease((t-1.05)/.85); draw.rounded_rectangle((575,468,575+770*line,474),radius=3,fill=alpha(LIGHT,opacity*.82))
    text(draw,(960,538),"DISTRICT INNOVATION · SHARED EVIDENCE · SUSTAINABLE IMPACT",bold(15),MIST,opacity*ease((t-1.45)/.85),"mm")
    text(draw,(960,604),"$7.05M IN COMPETITIVE AWARDS · 32 AWARD SELECTIONS",regular(20),LIGHT,opacity*ease((t-2)/.85),"mm")
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
