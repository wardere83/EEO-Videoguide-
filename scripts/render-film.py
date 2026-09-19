"""Render the silent cinematic EEO IBP initiative film."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
import math
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public/media"
OUT.mkdir(exist_ok=True)
FONTS = ROOT / "public/fonts"
FFMPEG = os.environ.get("FFMPEG") or str(ROOT / "node_modules/ffmpeg-static/ffmpeg")

W, H, FPS = 1280, 720, 24
DEEP = (1, 10, 25)
BLUE = (0, 102, 186)
CYAN = (72, 205, 255)
GOLD = (255, 182, 0)
WHITE = (246, 249, 252)
MIST = (176, 203, 228)

regular = lambda size: ImageFont.truetype(str(FONTS / "font-2.ttf"), size)
serif = lambda size: ImageFont.truetype(str(FONTS / "font-0.ttf"), size)
bold = lambda size: ImageFont.truetype(str(FONTS / "font-4.ttf"), size)

scenes = json.loads((ROOT / "src/film.json").read_text())
districts = json.loads((ROOT / "src/grantees.json").read_text())
TOTAL_DURATION = sum(scene["duration"] for scene in scenes)
STARS = [(((i * 197) % 1277) / 1277, ((i * 83 + 71) % 719) / 719, .18 + ((i * 47) % 100) / 125, 1 + i % 3) for i in range(72)]


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def ease(value):
    value = clamp(value)
    return 1 - (1 - value) ** 3


def alpha(color, opacity):
    return (*color, int(255 * clamp(opacity)))


def fade_window(local, duration, edge=.65):
    return min(ease(local / edge), ease((duration - local) / edge))


def wrap(draw, text, font, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and draw.textlength(trial, font=font) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def text_block(draw, text, x, y, font, fill, width, gap=1.12):
    for line in wrap(draw, text, font, width):
        draw.text((x, y), line, font=font, fill=fill)
        y += int(font.size * gap)
    return y


def reveal_text(im, text, xy, font, fill, progress, anchor="mm"):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text(xy, text, font=font, fill=fill, anchor=anchor)
    bbox = ld.textbbox(xy, text, font=font, anchor=anchor)
    reveal_x = int(bbox[0] + (bbox[2] - bbox[0]) * ease(progress))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rectangle((bbox[0] - 8, bbox[1] - 8, reveal_x + 8, bbox[3] + 8), fill=255)
    im.alpha_composite(Image.composite(layer, Image.new("RGBA", (W, H)), mask))


def base_frame(frame_no):
    t = frame_no / FPS
    im = Image.new("RGBA", (W, H), DEEP + (255,))
    draw = ImageDraw.Draw(im, "RGBA")
    for y in range(H):
        mix = y / H
        pulse = .5 + .5 * math.sin(t * .13)
        color = (int(2 + 2 * pulse), int(14 + 16 * (1 - mix)), int(31 + 43 * (1 - mix)), 255)
        draw.line((0, y, W, y), fill=color)
    vx = 640 + math.sin(t * .19) * 55
    vy = 365 + math.cos(t * .16) * 25
    for ring, opacity in ((390, .025), (295, .035), (205, .05)):
        draw.ellipse((vx - ring, vy - ring, vx + ring, vy + ring), outline=alpha(CYAN, opacity), width=2)
    for i, (sx, sy, depth, size) in enumerate(STARS):
        z = ((depth - t * (.018 + i % 4 * .002)) % .92) + .08
        x = 640 + (sx * W - 640) / z * .45
        y = 360 + (sy * H - 360) / z * .45
        if 4 < x < W - 4 and 4 < y < H - 4:
            opacity = clamp((1 - z) * .75 + .1)
            radius = size * (1.15 - z * .5)
            color = GOLD if i % 13 == 0 else CYAN
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=alpha(color, opacity))
    horizon = 585
    for i in range(8):
        gy = horizon + int((i / 8) ** 1.75 * 150)
        draw.line((0, gy, W, gy), fill=alpha(CYAN, .018), width=1)
    for i in range(-9, 10):
        draw.line((640, horizon, 640 + i * 145, H), fill=alpha(CYAN, .014), width=1)
    return im


def glow_core(draw, cx, cy, radius, t, opacity=1, color=BLUE):
    pulse = 1 + .045 * math.sin(t * 2.2)
    for step in range(5, 0, -1):
        r = radius * pulse + step * 18
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=alpha(color, opacity * (.035 + (5 - step) * .008)), width=2)
    for step in range(28, 0, -1):
        r = radius * pulse * step / 28
        mix = step / 28
        fill = (int(8 + (color[0] - 8) * (1 - mix) * .45), int(24 + (color[1] - 24) * (1 - mix) * .55), int(47 + (color[2] - 47) * (1 - mix) * .65))
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=alpha(fill, opacity))
    draw.arc((cx - radius, cy - radius, cx + radius, cy + radius), -75 + t * 15, 165 + t * 15, fill=alpha(GOLD, opacity), width=3)
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=alpha(MIST, opacity * .34), width=1)


def orbit(draw, cx, cy, rx, ry, angle, t, opacity=1, dots=2):
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=alpha(MIST, opacity * .18), width=2)
    for dot in range(dots):
        theta = t * (.55 + dot * .11) + angle + dot * math.pi
        x = cx + math.cos(theta) * rx
        y = cy + math.sin(theta) * ry
        r = 4 if dot == 0 else 3
        draw.ellipse((x-r, y-r, x+r, y+r), fill=alpha(GOLD if dot == 0 else CYAN, opacity))


def glass_panel(draw, box, title, value, opacity=1, accent=CYAN):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=14, fill=alpha((5, 26, 52), opacity * .78), outline=alpha(MIST, opacity * .22), width=1)
    draw.line((x1 + 15, y1 + 14, x1 + 48, y1 + 14), fill=alpha(accent, opacity), width=3)
    draw.text((x1 + 15, y1 + 28), title.upper(), font=bold(10), fill=alpha(MIST, opacity * .72))
    draw.text((x1 + 15, y1 + 50), value, font=bold(16), fill=alpha(WHITE, opacity))


def opener(im, draw, scene, local, duration, global_t):
    opacity = fade_window(local, duration)
    arrival = ease(local / 1.8)
    cx, cy = 640, 345
    glow_core(draw, cx, cy, 78 + arrival * 10, global_t, opacity)
    for index, (rx, ry) in enumerate(((165, 62), (225, 95), (292, 128))):
        orbit(draw, cx, cy, rx, ry, index * .8, global_t * (1 if index % 2 else -1), opacity, 2)
    if local > 1.0:
        reveal_text(im, "IDEAS BECOME", (640, 215), bold(15), alpha(GOLD, opacity), (local - 1) / 1.2)
    if local > 1.6:
        reveal_text(im, "INFRASTRUCTURE.", (640, 495), serif(68), alpha(WHITE, opacity), (local - 1.6) / 1.5)
    draw.text((640, 555), "Investment · people · practice · lasting opportunity", font=regular(16), fill=alpha(MIST, opacity * ease((local - 2.5) / 1.2)), anchor="mm")


def foundation(im, draw, scene, local, duration, global_t):
    opacity = fade_window(local, duration)
    arrival = ease(local / 1.3)
    cx, cy = 640, 350
    for i in range(7):
        radius = 92 + i * 47 + ((global_t * 28) % 47)
        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline=alpha(CYAN, opacity * (.18 - i * .018)), width=2)
    glow_core(draw, cx, cy, 113, global_t, opacity, BLUE)
    draw.text((cx, cy - 25), "$20M", font=serif(79), fill=alpha(WHITE, opacity * arrival), anchor="mm")
    draw.text((cx, cy + 42), "STATEWIDE EEO FOUNDATION · 2021", font=bold(12), fill=alpha(GOLD, opacity * arrival), anchor="mm")
    glass_panel(draw, (110, 170, 355, 255), "Fund established", "AB 132", opacity * ease((local - .7) / 1.1), GOLD)
    glass_panel(draw, (925, 440, 1170, 525), "Apportioned", "$15.5M systemwide", opacity * ease((local - 1.2) / 1.1), CYAN)
    draw.text((640, 610), "A foundation for district-led innovation", font=regular(18), fill=alpha(MIST, opacity), anchor="mm")


def first_awards(im, draw, scene, local, duration, global_t):
    opacity = fade_window(local, duration)
    arrival = ease(local / 1.4)
    for i in range(21):
        angle = i * (math.pi * 2 / 21) + global_t * .08
        radius = 130 + (i % 4) * 58
        x = 640 + math.cos(angle) * radius * 1.45
        y = 360 + math.sin(angle) * radius * .72
        reveal = ease((local - i * .035) / .85)
        draw.line((640, 360, x, y), fill=alpha(CYAN, opacity * reveal * .11), width=1)
        r = 3 + (i % 3)
        draw.ellipse((x-r, y-r, x+r, y+r), fill=alpha(GOLD if i % 5 == 0 else CYAN, opacity * reveal))
    glow_core(draw, 640, 360, 101, global_t, opacity)
    draw.text((640, 338), "$5.65M", font=serif(66), fill=alpha(WHITE, opacity * arrival), anchor="mm")
    draw.text((640, 395), "21 DISTRICT AWARDS", font=bold(12), fill=alpha(GOLD, opacity * arrival), anchor="mm")
    draw.text((640, 112), "THE FIRST COMPETITIVE CYCLE", font=bold(14), fill=alpha(MIST, opacity), anchor="mm")
    draw.text((640, 625), "Twenty-one signals of possibility · 2023–25", font=regular(18), fill=alpha(MIST, opacity), anchor="mm")


def current_cycle(im, draw, scene, local, duration, global_t):
    opacity = fade_window(local, duration)
    arrival = ease(local / 1.2)
    cx, cy = 640, 360
    glow_core(draw, cx, cy, 91, global_t, opacity)
    draw.text((cx, cy - 20), "$1.4M", font=serif(58), fill=alpha(WHITE, opacity * arrival), anchor="mm")
    draw.text((cx, cy + 32), "2026–28", font=bold(12), fill=alpha(GOLD, opacity), anchor="mm")
    for index, district in enumerate(districts):
        angle = -math.pi / 2 + index * (2 * math.pi / len(districts)) + math.sin(global_t * .18) * .025
        x, y = cx + math.cos(angle) * 420, cy + math.sin(angle) * 225
        reveal = ease((local - index * .06) / .9)
        draw.line((cx, cy, x, y), fill=alpha(MIST, opacity * reveal * .2), width=1)
        travel = (global_t * .18 + index / len(districts)) % 1
        px, py = cx + (x-cx) * travel, cy + (y-cy) * travel
        draw.ellipse((px-3, py-3, px+3, py+3), fill=alpha(GOLD, opacity * reveal))
        box = (x-70, y-25, x+70, y+25)
        draw.rounded_rectangle(box, radius=12, fill=alpha((3, 23, 49), opacity * reveal * .92), outline=alpha(CYAN, opacity * reveal * .28), width=1)
        draw.text((x, y-7), district["shortName"], font=bold(10), fill=alpha(WHITE, opacity * reveal), anchor="mm")
        draw.text((x, y+11), f'${district["award"] // 1000}K', font=bold(12), fill=alpha(GOLD, opacity * reveal), anchor="mm")
    draw.text((640, 91), "ELEVEN DISTRICTS · ONE CONNECTED COHORT", font=bold(14), fill=alpha(MIST, opacity), anchor="mm")
    draw.text((640, 650), "Every award visible. Every project connected.", font=regular(16), fill=alpha(MIST, opacity), anchor="mm")


def combined_impact(im, draw, scene, local, duration, global_t):
    opacity = fade_window(local, duration)
    arrival = ease(local / 1.3)
    draw.text((640, 115), "COMPETITIVE AWARDS SINCE LAUNCH", font=bold(14), fill=alpha(GOLD, opacity), anchor="mm")
    draw.text((640, 285), "$7.05M", font=serif(128), fill=alpha(WHITE, opacity * arrival), anchor="mm")
    draw.text((640, 365), "32 AWARD SELECTIONS · TWO CYCLES", font=bold(15), fill=alpha(MIST, opacity), anchor="mm")
    words = [("RECRUIT", 265, 500), ("MENTOR", 500, 540), ("BELONG", 775, 540), ("GROW", 1015, 500)]
    for index, (word, x, y) in enumerate(words):
        drift = math.sin(global_t * .7 + index) * 8
        draw.rounded_rectangle((x-83, y-25+drift, x+83, y+25+drift), radius=25, fill=alpha((4, 30, 61), opacity * .8), outline=alpha(CYAN if index % 2 else GOLD, opacity * .4), width=1)
        draw.text((x, y+drift), word, font=bold(13), fill=alpha(WHITE, opacity), anchor="mm")
    orbit(draw, 640, 330, 485, 230, .2, global_t * .5, opacity, 4)


def local_signals(im, draw, scene, local, duration, global_t):
    opacity = fade_window(local, duration)
    reveal = ease(local / 1.3)
    draw.text((95, 115), "LOCAL IDEAS · SYSTEMWIDE LEARNING", font=bold(14), fill=alpha(GOLD, opacity))
    draw.text((90, 165), "Impact moves", font=serif(66), fill=alpha(WHITE, opacity * reveal))
    draw.text((90, 228), "through people.", font=serif(66), fill=alpha(WHITE, opacity * reveal))
    panels = [("INCLUSIVE HIRING", "Remove barriers", 700, 140), ("MENTORSHIP", "Grow leadership", 865, 315), ("FACULTY PATHWAYS", "Expand access", 690, 500), ("BELONGING", "Strengthen culture", 390, 455)]
    for index, (title, detail, x, y) in enumerate(panels):
        angle = global_t * .34 + index * math.pi / 2
        px, py = x + math.cos(angle) * 18, y + math.sin(angle) * 11
        panel_opacity = opacity * ease((local - index * .18) / 1.0)
        glass_panel(draw, (px, py, px+270, py+96), title, detail, panel_opacity, GOLD if index % 2 == 0 else CYAN)
        draw.line((640, 365, px+135, py+48), fill=alpha(MIST, panel_opacity * .18), width=1)
    glow_core(draw, 640, 365, 54, global_t, opacity, GOLD)
    draw.text((640, 365), "EEO", font=serif(28), fill=alpha(WHITE, opacity), anchor="mm")


def sustainable(im, draw, scene, local, duration, global_t):
    opacity = fade_window(local, duration)
    arrival = ease(local / 1.2)
    cx, cy = 640, 370
    for index in range(7):
        radius = 75 + index * 48 + math.sin(global_t * .7 + index) * 7
        start = -90 + global_t * (12 if index % 2 else -10) + index * 25
        draw.arc((cx-radius, cy-radius, cx+radius, cy+radius), start, start+215, fill=alpha(CYAN if index % 2 else GOLD, opacity * (.72-index*.07)), width=3 if index < 2 else 2)
    glow_core(draw, cx, cy, 72, global_t, opacity)
    stages = [("INVEST", -1.72), ("TEST", -.48), ("LEARN", .63), ("SUSTAIN", 1.95)]
    for label, angle in stages:
        theta = angle + global_t * .08
        x, y = cx + math.cos(theta) * 300, cy + math.sin(theta) * 185
        draw.ellipse((x-42, y-42, x+42, y+42), fill=alpha((3, 25, 52), opacity * .92), outline=alpha(GOLD if label == "SUSTAIN" else MIST, opacity * .5), width=2)
        draw.text((x, y), label, font=bold(11), fill=alpha(GOLD if label == "SUSTAIN" else WHITE, opacity), anchor="mm")
    draw.text((cx, cy-12), "IMPACT", font=bold(13), fill=alpha(GOLD, opacity * arrival), anchor="mm")
    draw.text((cx, cy+16), "COMPOUNDS", font=bold(13), fill=alpha(WHITE, opacity * arrival), anchor="mm")
    draw.text((640, 105), "A SUSTAINABLE IMPACT LOOP", font=bold(14), fill=alpha(MIST, opacity), anchor="mm")
    draw.text((640, 630), "Projects become practice. Practice becomes shared capacity.", font=regular(18), fill=alpha(MIST, opacity), anchor="mm")


def finale(im, draw, scene, local, duration, global_t):
    opacity = fade_window(local, duration, .45)
    assemble = ease(local / 2.1)
    cx, cy = 640, 335
    for index, radius in enumerate((145, 220, 305)):
        orbit(draw, cx, cy, radius, int(radius*.34), index * .8, global_t * (1 if index % 2 else -1), opacity, 2)
    glow_core(draw, cx, cy, 57, global_t, opacity * .8)
    final_x = [515, 640, 765]
    starts = [(-120, 200), (640, -120), (1400, 470)]
    for index, letter in enumerate("IBP"):
        stagger = ease((assemble - index * .09) / .82)
        x = starts[index][0] + (final_x[index] - starts[index][0]) * stagger
        y = starts[index][1] + (cy - starts[index][1]) * stagger
        draw.text((x, y), letter, font=serif(150), fill=alpha(WHITE, opacity * stagger), anchor="mm")
    line_progress = ease((local - 1.6) / 1.3)
    draw.line((430, 449, 430 + 420 * line_progress, 449), fill=alpha(GOLD, opacity), width=4)
    if local > 1.8:
        reveal_text(im, "GRANT INITIATIVE", (640, 492), bold(25), alpha(WHITE, opacity), (local - 1.8) / 1.4)
    draw.text((640, 555), "IDEAS · PRACTICE · EVIDENCE · SUSTAINABLE IMPACT", font=bold(11), fill=alpha(MIST, opacity * ease((local - 2.8) / 1.2)), anchor="mm")


def render_scene(index, local, frame_no):
    im = base_frame(frame_no)
    draw = ImageDraw.Draw(im, "RGBA")
    renderers = [opener, foundation, first_awards, current_cycle, combined_impact, local_signals, sustainable, finale]
    renderers[index](im, draw, scenes[index], local, scenes[index]["duration"], frame_no / FPS)
    return im.convert("RGB")


def timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int(seconds // 60 % 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def main():
    if not Path(FFMPEG).exists():
        raise SystemExit(f"ffmpeg not found at {FFMPEG}")
    frame_total = int(TOTAL_DURATION * FPS)
    mp4 = OUT / "eeo-initiative.mp4"
    command = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    starts, elapsed = [], 0
    for scene in scenes:
        starts.append(elapsed)
        elapsed += scene["duration"]
    poster_saved = False
    for frame_no in range(frame_total):
        current = frame_no / FPS
        index = max(i for i, start in enumerate(starts) if start <= current)
        image = render_scene(index, current - starts[index], frame_no)
        if not poster_saved and current >= 3.2:
            image.save(OUT / "eeo-poster.jpg", quality=95)
            poster_saved = True
        process.stdin.write(image.tobytes())
        if frame_no % (FPS * 5) == 0:
            print(f"Rendered {frame_no // FPS:02d}s / {TOTAL_DURATION}s", flush=True)
    process.stdin.close()
    if process.wait() != 0:
        raise SystemExit("MP4 render failed")
    webm = OUT / "eeo-initiative.webm"
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", str(mp4), "-an", "-c:v", "libvpx-vp9", "-crf", "31", "-b:v", "0", "-deadline", "good", "-cpu-used", "3", str(webm)], check=True)
    captions = ["WEBVTT", ""]
    elapsed = 0
    for scene in scenes:
        end = elapsed + scene["duration"]
        captions.extend([f"{timestamp(elapsed)} --> {timestamp(end)}", scene["title"].replace("\n", " "), scene.get("transcript", scene["description"]).replace("\n", " "), ""])
        elapsed = end
    (OUT / "eeo-initiative.en.vtt").write_text("\n".join(captions))
    print(f"Complete: {TOTAL_DURATION}s silent cinematic film", flush=True)


if __name__ == "__main__":
    main()
