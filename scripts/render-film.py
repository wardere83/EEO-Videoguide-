"""Render the silent cinematic EEO IBP initiative film."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import json
import math
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public/media"
FONTS = ROOT / "public/fonts"
FFMPEG = os.environ.get("FFMPEG") or str(ROOT / "node_modules/ffmpeg-static/ffmpeg")
W, H, FPS = 1280, 720, 24
WHITE, GOLD, MIST, CYAN = (248, 250, 252), (255, 182, 0), (184, 205, 225), (96, 201, 241)

regular = lambda size: ImageFont.truetype(str(FONTS / "font-2.ttf"), size)
serif = lambda size: ImageFont.truetype(str(FONTS / "font-0.ttf"), size)
bold = lambda size: ImageFont.truetype(str(FONTS / "font-4.ttf"), size)
scenes = json.loads((ROOT / "src/film.json").read_text())
TOTAL_DURATION = sum(scene["duration"] for scene in scenes)

plate_dir = OUT / "cinematic"
PLATES = {
    "core": Image.open(plate_dir / "california-core.png").convert("RGB"),
    "network": Image.open(plate_dir / "district-network.png").convert("RGB"),
    "people": Image.open(plate_dir / "people-impact.png").convert("RGB"),
    "future": Image.open(plate_dir / "sustainable-future.png").convert("RGB"),
}
PARTICLES = [(((i * 193) % 1279), ((i * 79 + 37) % 719), 1 + i % 3, .24 + (i % 7) * .05) for i in range(48)]


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def ease(value):
    value = clamp(value)
    return 1 - (1 - value) ** 3


def smooth(value):
    value = clamp(value)
    return value * value * (3 - 2 * value)


def alpha(color, opacity):
    return (*color, int(255 * clamp(opacity)))


def fade_window(local, duration, edge=.55):
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


def shadow_text(draw, xy, text, font, fill, anchor=None, shadow=180):
    x, y = xy
    draw.text((x + 2, y + 3), text, font=font, fill=(0, 0, 0, shadow), anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)


def plate_frame(key, local, duration, pan=(0, 0), zoom=(1.03, 1.12), darkness=.12):
    source = PLATES[key]
    progress = smooth(local / duration)
    scale = zoom[0] + (zoom[1] - zoom[0]) * progress
    target_w, target_h = int(W * scale), int(H * scale)
    image = source.resize((target_w, target_h), Image.Resampling.LANCZOS)
    travel_x = int(pan[0] * (progress - .5))
    travel_y = int(pan[1] * (progress - .5))
    left = max(0, min(target_w - W, (target_w - W) // 2 + travel_x))
    top = max(0, min(target_h - H, (target_h - H) // 2 + travel_y))
    image = image.crop((left, top, left + W, top + H))
    image = ImageEnhance.Contrast(image).enhance(1.08)
    image = ImageEnhance.Color(image).enhance(.94)
    overlay = Image.new("RGBA", (W, H), (0, 16, 38, int(255 * darkness)))
    return Image.alpha_composite(image.convert("RGBA"), overlay)


def atmosphere(im, global_t, opacity=1):
    # Draw atmospheric elements on a separate layer so their alpha is
    # composited instead of becoming opaque when the final frame is flattened.
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for index, (x0, y0, size, base_opacity) in enumerate(PARTICLES):
        x = (x0 + global_t * (5 + index % 5)) % (W + 80) - 40
        y = y0 + math.sin(global_t * .35 + index) * 12
        draw.ellipse((x-size, y-size, x+size, y+size), fill=alpha(GOLD if index % 9 == 0 else CYAN, base_opacity * opacity))
    sweep = int((global_t * 95) % (W + 500)) - 250
    draw.polygon([(sweep, 0), (sweep+95, 0), (sweep+380, H), (sweep+260, H)], fill=alpha((130, 211, 255), .018 * opacity))
    draw.rectangle((0, 0, W, 22), fill=(0, 0, 0, 235))
    draw.rectangle((0, H-22, W, H), fill=(0, 0, 0, 235))
    im.alpha_composite(layer)


def left_gradient(im, strength=.68, width=760):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for x in range(width):
        opacity = strength * (1 - x / width) ** 1.55
        draw.line((x, 0, x, H), fill=(0, 7, 18, int(255 * opacity)))
    im.alpha_composite(layer)


def lower_gradient(im, strength=.75, height=330):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for offset in range(height):
        y = H - offset
        opacity = strength * (1 - offset / height) ** 1.7
        draw.line((0, y, W, y), fill=(0, 6, 16, int(255 * opacity)))
    im.alpha_composite(layer)


def title_lockup(draw, kicker, title, detail, opacity, x=86, y=410, width=690):
    shadow_text(draw, (x, y), kicker.upper(), bold(14), alpha(GOLD, opacity))
    title_font = serif(66)
    cursor = y + 42
    for line in wrap(draw, title, title_font, width):
        shadow_text(draw, (x, cursor), line, title_font, alpha(WHITE, opacity), shadow=210)
        cursor += 62
    draw.line((x, cursor + 9, x + 88, cursor + 9), fill=alpha(GOLD, opacity), width=4)
    shadow_text(draw, (x, cursor + 31), detail, regular(18), alpha(MIST, opacity), shadow=210)


def number_lockup(draw, amount, label, detail, opacity, x=90, y=285):
    shadow_text(draw, (x, y), label.upper(), bold(14), alpha(GOLD, opacity))
    shadow_text(draw, (x, y + 48), amount, serif(104), alpha(WHITE, opacity), shadow=220)
    draw.line((x, y + 154, x + 112, y + 154), fill=alpha(GOLD, opacity), width=4)
    shadow_text(draw, (x, y + 181), detail, regular(19), alpha(MIST, opacity), shadow=210)


def finish_scene(im, local, duration, global_t):
    opacity = fade_window(local, duration)
    atmosphere(im, global_t, opacity)
    if opacity < 1:
        fade = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1-opacity))))
        im.alpha_composite(fade)
    return im.convert("RGB")


def opener(local, duration, global_t):
    im = plate_frame("core", local, duration, pan=(38, -8), zoom=(1.01, 1.095), darkness=.13)
    lower_gradient(im, .72, 310)
    draw = ImageDraw.Draw(im, "RGBA")
    opacity = fade_window(local, duration) * ease((local-.45)/1.1)
    title_lockup(draw, "Equal employment opportunity", "Ideas become infrastructure.", "Investment · people · practice · lasting opportunity", opacity, x=86, y=425, width=760)
    return finish_scene(im, local, duration, global_t)


def foundation(local, duration, global_t):
    im = plate_frame("core", local, duration, pan=(-55, 8), zoom=(1.08, 1.18), darkness=.18)
    left_gradient(im, .78)
    draw = ImageDraw.Draw(im, "RGBA")
    opacity = fade_window(local, duration) * ease(local/1.0)
    number_lockup(draw, "$20M", "The foundation · 2021", "$15.5M apportioned systemwide", opacity)
    return finish_scene(im, local, duration, global_t)


def first_cycle(local, duration, global_t):
    im = plate_frame("network", local, duration, pan=(45, -16), zoom=(1.04, 1.135), darkness=.2)
    left_gradient(im, .82)
    draw = ImageDraw.Draw(im, "RGBA")
    opacity = fade_window(local, duration) * ease(local/1.0)
    number_lockup(draw, "$5.65M", "First competitive cycle · 2023–25", "21 district awards", opacity)
    return finish_scene(im, local, duration, global_t)


def current_cycle(local, duration, global_t):
    im = plate_frame("network", local, duration, pan=(-45, 10), zoom=(1.01, 1.10), darkness=.08)
    lower_gradient(im, .82, 280)
    draw = ImageDraw.Draw(im, "RGBA")
    opacity = fade_window(local, duration) * ease(local/1.0)
    shadow_text(draw, (640, 525), "$1.4M", serif(92), alpha(WHITE, opacity), anchor="mm", shadow=230)
    shadow_text(draw, (640, 588), "ELEVEN DISTRICTS · 2026–28", bold(15), alpha(GOLD, opacity), anchor="mm", shadow=220)
    shadow_text(draw, (640, 622), "Every award visible. Every project connected.", regular(17), alpha(MIST, opacity), anchor="mm", shadow=220)
    return finish_scene(im, local, duration, global_t)


def combined(local, duration, global_t):
    im = plate_frame("core", local, duration, pan=(0, -22), zoom=(1.13, 1.25), darkness=.28)
    lower_gradient(im, .88, 370)
    draw = ImageDraw.Draw(im, "RGBA")
    opacity = fade_window(local, duration) * ease(local/1.0)
    shadow_text(draw, (640, 424), "$7.05M", serif(122), alpha(WHITE, opacity), anchor="mm", shadow=240)
    shadow_text(draw, (640, 500), "COMPETITIVE AWARDS SINCE LAUNCH", bold(15), alpha(GOLD, opacity), anchor="mm", shadow=230)
    shadow_text(draw, (640, 545), "32 award selections · two cycles", regular(20), alpha(MIST, opacity), anchor="mm", shadow=220)
    return finish_scene(im, local, duration, global_t)


def people(local, duration, global_t):
    im = plate_frame("people", local, duration, pan=(42, -10), zoom=(1.01, 1.09), darkness=.09)
    lower_gradient(im, .9, 315)
    draw = ImageDraw.Draw(im, "RGBA")
    opacity = fade_window(local, duration) * ease(local/1.0)
    title_lockup(draw, "Local ideas · systemwide learning", "Impact moves through people.", "Inclusive hiring · mentorship · faculty pathways · belonging", opacity, x=78, y=438, width=820)
    return finish_scene(im, local, duration, global_t)


def sustainable(local, duration, global_t):
    im = plate_frame("future", local, duration, pan=(-24, -16), zoom=(1.01, 1.10), darkness=.14)
    lower_gradient(im, .86, 320)
    draw = ImageDraw.Draw(im, "RGBA")
    opacity = fade_window(local, duration) * ease(local/1.0)
    title_lockup(draw, "Sustainable impact", "Investment that compounds.", "INVEST  →  TEST  →  LEARN  →  SUSTAIN", opacity, x=82, y=438, width=820)
    return finish_scene(im, local, duration, global_t)


def finale(local, duration, global_t):
    im = plate_frame("future", local, duration, pan=(0, -8), zoom=(1.10, 1.20), darkness=.18)
    darken = ease(local / 2.2) * .66
    ImageDraw.Draw(im, "RGBA").rectangle((0, 0, W, H), fill=(0, 9, 24, int(255 * darken)))
    draw = ImageDraw.Draw(im, "RGBA")
    opacity = fade_window(local, duration, .4)
    assemble = ease(local / 2.25)
    starts = [(-140, 260), (640, -140), (1420, 440)]
    final_x = [510, 640, 770]
    for index, letter in enumerate("IBP"):
        progress = ease((assemble-index*.08)/.84)
        x = starts[index][0] + (final_x[index]-starts[index][0])*progress
        y = starts[index][1] + (320-starts[index][1])*progress
        shadow_text(draw, (x, y), letter, serif(158), alpha(WHITE, opacity*progress), anchor="mm", shadow=245)
    line = ease((local-1.5)/1.2)
    draw.line((430, 438, 430+420*line, 438), fill=alpha(GOLD, opacity), width=4)
    if local > 1.8:
        shadow_text(draw, (640, 482), "GRANT INITIATIVE", bold(27), alpha(WHITE, opacity*ease((local-1.8)/1.1)), anchor="mm", shadow=240)
    shadow_text(draw, (640, 535), "IDEAS · PRACTICE · EVIDENCE · SUSTAINABLE IMPACT", bold(11), alpha(MIST, opacity*ease((local-2.7)/1.0)), anchor="mm", shadow=230)
    return finish_scene(im, local, duration, global_t)


RENDERERS = [opener, foundation, first_cycle, current_cycle, combined, people, sustainable, finale]


def timestamp(seconds):
    hours, minutes, secs = int(seconds//3600), int(seconds//60%60), int(seconds%60)
    millis = int(round((seconds-int(seconds))*1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def main():
    if not Path(FFMPEG).exists():
        raise SystemExit(f"ffmpeg not found at {FFMPEG}")
    OUT.mkdir(exist_ok=True)
    mp4 = OUT / "eeo-initiative.mp4"
    command = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    starts, elapsed = [], 0
    for scene in scenes:
        starts.append(elapsed)
        elapsed += scene["duration"]
    poster_saved = False
    for frame_no in range(int(TOTAL_DURATION*FPS)):
        current = frame_no/FPS
        index = max(i for i, start in enumerate(starts) if start <= current)
        local = current-starts[index]
        image = RENDERERS[index](local, scenes[index]["duration"], current)
        if not poster_saved and current >= 3.4:
            image.save(OUT / "eeo-poster.jpg", quality=96)
            poster_saved = True
        process.stdin.write(image.tobytes())
        if frame_no % (FPS*5) == 0:
            print(f"Rendered {frame_no//FPS:02d}s / {TOTAL_DURATION}s", flush=True)
    process.stdin.close()
    if process.wait() != 0:
        raise SystemExit("MP4 render failed")
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", str(mp4), "-an", "-c:v", "libvpx-vp9", "-crf", "29", "-b:v", "0", "-deadline", "good", "-cpu-used", "3", str(OUT/"eeo-initiative.webm")], check=True)
    captions, elapsed = ["WEBVTT", ""], 0
    for scene in scenes:
        end = elapsed+scene["duration"]
        captions.extend([f"{timestamp(elapsed)} --> {timestamp(end)}", scene["title"], scene.get("transcript", scene["description"]), ""])
        elapsed = end
    (OUT/"eeo-initiative.en.vtt").write_text("\n".join(captions))
    print(f"Complete: {TOTAL_DURATION}s silent cinematic film", flush=True)


if __name__ == "__main__":
    main()
