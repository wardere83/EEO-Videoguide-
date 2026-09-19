"""Render a silent, full-motion EEO IBP funding story.

Run from the repository root after installing dependencies. The output contains
video only—no audio stream—and is written in MP4 and WebM formats.
"""

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
NAVY = (0, 39, 85)
DEEP = (0, 20, 50)
BLUE = (0, 70, 135)
GOLD = (255, 182, 0)
WHITE = (248, 251, 255)
MIST = (200, 218, 235)

regular = lambda size: ImageFont.truetype(str(FONTS / "font-2.ttf"), size)
serif = lambda size: ImageFont.truetype(str(FONTS / "font-0.ttf"), size)
bold = lambda size: ImageFont.truetype(str(FONTS / "font-4.ttf"), size)

scenes = json.loads((ROOT / "src/film.json").read_text())
districts = json.loads((ROOT / "src/grantees.json").read_text())
logo = Image.open(ROOT / "public/brand/cccco-logo.png").convert("RGBA")
logo.thumbnail((330, 48))


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def ease(value):
    value = clamp(value)
    return 1 - (1 - value) ** 3


def fade_window(t, duration):
    return min(ease(t / 0.8), ease((duration - t) / 0.8))


def alpha(color, opacity):
    return (*color, int(255 * clamp(opacity)))


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


def text_block(draw, text, x, y, font, fill, width, gap=1.12, anchor=None):
    for line in wrap(draw, text, font, width):
        draw.text((x, y), line, font=font, fill=fill, anchor=anchor)
        y += int(font.size * gap)
    return y


def background(frame_no):
    im = Image.new("RGB", (W, H), DEEP)
    draw = ImageDraw.Draw(im)
    for y in range(H):
        mix = y / H
        color = tuple(int(NAVY[i] * (1 - mix) + DEEP[i] * mix) for i in range(3))
        draw.line((0, y, W, y), fill=color)

    phase = frame_no / FPS
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    cx = 1010 + 55 * math.sin(phase * 0.22)
    cy = 355 + 38 * math.cos(phase * 0.18)
    for radius, opacity in ((330, .05), (245, .07), (155, .09)):
        od.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=alpha(MIST, opacity), width=2)
    for i in range(7):
        offset = (phase * (22 + i * 2) + i * 180) % 1500 - 120
        od.line((offset, H, offset + 450, 0), fill=alpha(BLUE, .18), width=1)
    for i in range(24):
        x = (i * 173 + phase * (8 + i % 4)) % W
        y = (i * 97 + 80 * math.sin(phase * .17 + i)) % H
        radius = 2 if i % 5 else 3
        od.ellipse((x - radius, y - radius, x + radius, y + radius), fill=alpha(GOLD if i % 6 == 0 else MIST, .38))
    return Image.alpha_composite(im.convert("RGBA"), overlay)


def brand(draw, im):
    draw.rounded_rectangle((36, 28, 405, 91), radius=32, fill=(255, 255, 255, 242))
    im.alpha_composite(logo, (57, 36))
    draw.text((1220, 47), "EEO IBP", font=bold(15), fill=alpha(WHITE, .76), anchor="ra")


def progress_line(draw, elapsed):
    draw.line((48, 680, 1232, 680), fill=alpha(MIST, .22), width=2)
    draw.line((48, 680, 48 + 1184 * elapsed / 78, 680), fill=GOLD, width=3)


def heading(draw, kicker, title, description, opacity, offset=0):
    fill = alpha(WHITE, opacity)
    draw.text((62, 160 + offset), kicker.upper(), font=bold(17), fill=alpha(GOLD, opacity))
    y = text_block(draw, title, 58, 208 + offset, serif(69), fill, 760, .98)
    draw.rounded_rectangle((62, y + 24, 148, y + 29), radius=3, fill=alpha(GOLD, opacity))
    text_block(draw, description, 62, y + 57, regular(25), alpha(MIST, opacity), 690, 1.3)


def funding_orbit(draw, amount, caption, progress, opacity):
    cx, cy = 1015, 370
    for i, radius in enumerate((92, 142, 196, 248)):
        start = -90 + i * 16 + progress * 40
        sweep = 170 + i * 24
        draw.arc((cx - radius, cy - radius, cx + radius, cy + radius), start=start, end=start + sweep, fill=alpha(GOLD if i == 0 else MIST, opacity * (.9 - i * .13)), width=5 if i == 0 else 2)
    count = progress
    if amount == "$20M":
        value = f"${20 * count:,.1f}M" if count < .98 else amount
    elif amount == "$5.65M":
        value = f"${5.651806 * count:,.2f}M" if count < .98 else amount
    elif amount == "$1.4M":
        value = f"${1.4 * count:,.1f}M" if count < .98 else amount
    else:
        value = f"${7.051806 * count:,.2f}M" if count < .98 else amount
    draw.text((cx, cy - 20), value, font=serif(65), fill=alpha(WHITE, opacity), anchor="mm")
    draw.text((cx, cy + 47), caption.upper(), font=bold(13), fill=alpha(MIST, opacity * .85), anchor="mm")


def funding_scene(draw, scene, local, duration, amount, caption, supporting):
    opacity = fade_window(local, duration)
    arrival = ease(local / 2)
    heading(draw, scene["label"], scene["title"], scene["description"], opacity * arrival, int((1 - arrival) * 22))
    funding_orbit(draw, amount, caption, arrival, opacity)
    draw.text((1015, 630), supporting, font=regular(16), fill=alpha(MIST, opacity * .8), anchor="mm")


def district_scene(draw, scene, local, duration):
    opacity = fade_window(local, duration)
    arrival = ease(local / 1.7)
    draw.text((62, 148), scene["label"], font=bold(17), fill=alpha(GOLD, opacity))
    draw.text((58, 188), scene["title"], font=serif(48), fill=alpha(WHITE, opacity * arrival))
    draw.text((60, 246), scene["description"], font=regular(18), fill=alpha(MIST, opacity * arrival))

    cx, cy = 640, 465
    positions = []
    for index, district in enumerate(districts):
        angle = -math.pi / 2 + index * (2 * math.pi / len(districts))
        positions.append((cx + math.cos(angle) * 500, cy + math.sin(angle) * 172))

    for index, (x, y) in enumerate(positions):
        reveal = ease((local - index * .09) / 1.1)
        draw.line((cx, cy, x, y), fill=alpha(MIST, opacity * reveal * .24), width=2)
        travel = (local * .32 + index / len(districts)) % 1
        px, py = cx + (x - cx) * travel, cy + (y - cy) * travel
        draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill=alpha(GOLD, opacity * reveal * .8))

    draw.ellipse((cx - 91, cy - 91, cx + 91, cy + 91), fill=alpha(DEEP, opacity * .96), outline=alpha(GOLD, opacity), width=3)
    draw.ellipse((cx - 108, cy - 108, cx + 108, cy + 108), outline=alpha(MIST, opacity * .22), width=2)
    draw.text((cx, cy - 23), "$1.4M", font=serif(48), fill=alpha(WHITE, opacity), anchor="mm")
    draw.text((cx, cy + 22), "11 DISTRICTS", font=bold(13), fill=alpha(GOLD, opacity), anchor="mm")
    draw.text((cx, cy + 46), "2026–28", font=regular(12), fill=alpha(MIST, opacity), anchor="mm")

    for index, (x, y) in enumerate(positions):
        district = districts[index]
        reveal = ease((local - index * .09) / 1.1)
        box = (x - 75, y - 28, x + 75, y + 28)
        draw.rounded_rectangle(box, radius=12, fill=alpha(NAVY, opacity * reveal * .96), outline=alpha(MIST, opacity * reveal * .36), width=1)
        draw.text((x, y - 8), district["shortName"], font=bold(12), fill=alpha(WHITE, opacity * reveal), anchor="mm")
        draw.text((x, y + 12), f'${district["award"] // 1000}K', font=bold(15), fill=alpha(GOLD, opacity * reveal), anchor="mm")


def render_scene(index, local, frame_no):
    scene = scenes[index]
    duration = scene["duration"]
    im = background(frame_no)
    draw = ImageDraw.Draw(im, "RGBA")
    brand(draw, im)

    if index == 0:
        opacity = fade_window(local, duration)
        arrival = ease(local / 2)
        heading(draw, scene["label"], scene["title"], scene["description"], opacity * arrival, int((1 - arrival) * 28))
        for i in range(5):
            radius = 74 + i * 46 + 10 * math.sin(local * .7 + i)
            draw.arc((1005 - radius, 360 - radius, 1005 + radius, 360 + radius), start=-120 + local * 12 + i * 20, end=80 + local * 12 + i * 20, fill=alpha(GOLD if i == 0 else MIST, opacity * (.85 - i * .12)), width=4 if i == 0 else 2)
        draw.text((1005, 355), "EEO", font=serif(70), fill=alpha(WHITE, opacity), anchor="mm")
    elif index == 1:
        funding_scene(draw, scene, local, duration, "$20M", "2021 foundation", "$15.5M apportioned systemwide")
    elif index == 2:
        funding_scene(draw, scene, local, duration, "$5.65M", "2023–25 awards", "21 district awards")
    elif index == 3:
        funding_scene(draw, scene, local, duration, "$1.4M", "2026–28 awards", "11 district awards")
    elif index == 4:
        funding_scene(draw, scene, local, duration, "$7.05M", "competitive awards since launch", "32 award selections · two cycles")
    elif index == 5:
        district_scene(draw, scene, local, duration)
    else:
        opacity = fade_window(local, duration)
        arrival = ease(local / 2)
        heading(draw, scene["label"], scene["title"], scene["description"], opacity * arrival, int((1 - arrival) * 26))
        draw.text((1004, 354), "$7.05M", font=serif(74), fill=alpha(WHITE, opacity), anchor="mm")
        draw.text((1004, 418), "COMPETITIVE AWARDS", font=bold(14), fill=alpha(GOLD, opacity), anchor="mm")

    elapsed = sum(s["duration"] for s in scenes[:index]) + local
    progress_line(draw, elapsed)
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

    total = sum(scene["duration"] for scene in scenes)
    frame_total = int(total * FPS)
    mp4 = OUT / "eeo-initiative.mp4"
    command = [
        FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(mp4),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    starts, elapsed = [], 0
    for scene in scenes:
        starts.append(elapsed)
        elapsed += scene["duration"]

    poster_saved = False
    for frame_no in range(frame_total):
        current = frame_no / FPS
        index = max(i for i, start in enumerate(starts) if start <= current)
        local = current - starts[index]
        image = render_scene(index, local, frame_no)
        if not poster_saved and current >= 2:
            image.save(OUT / "eeo-poster.jpg", quality=94)
            poster_saved = True
        process.stdin.write(image.tobytes())
        if frame_no % (FPS * 5) == 0:
            print(f"Rendered {frame_no // FPS:02d}s / {total}s", flush=True)
    process.stdin.close()
    if process.wait() != 0:
        raise SystemExit("MP4 render failed")

    webm = OUT / "eeo-initiative.webm"
    subprocess.run([
        FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", str(mp4), "-an",
        "-c:v", "libvpx-vp9", "-crf", "34", "-b:v", "0", "-deadline", "good", "-cpu-used", "4", str(webm),
    ], check=True)

    captions = ["WEBVTT", ""]
    elapsed = 0
    for scene in scenes:
        end = elapsed + scene["duration"]
        captions.extend([
            f"{timestamp(elapsed)} --> {timestamp(end)}",
            scene["title"].replace("\n", " "),
            scene.get("transcript", scene["description"]).replace("\n", " "),
            "",
        ])
        elapsed = end
    (OUT / "eeo-initiative.en.vtt").write_text("\n".join(captions))
    print(f"Complete: {total}s silent motion film", flush=True)


if __name__ == "__main__":
    main()
