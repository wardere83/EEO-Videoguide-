"""Render the silent, academic EEO IBP initiative explainer."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
import math
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public/media"
FONTS = ROOT / "public/fonts"
FFMPEG = os.environ.get("FFMPEG") or str(ROOT / "node_modules/ffmpeg-static/ffmpeg")
W, H, FPS = 1280, 720, 24
NAVY = (0, 47, 109)
DARK_BLUE = (0, 39, 85)
MEDIUM_BLUE = (0, 102, 186)
LIGHT_BLUE = (64, 180, 229)
GOLD = (255, 182, 0)
GREY = (85, 87, 89)
PALE = (242, 247, 251)
WHITE = (255, 255, 255)

regular = lambda size: ImageFont.truetype(str(FONTS / "font-2.ttf"), size)
serif = lambda size: ImageFont.truetype(str(FONTS / "font-0.ttf"), size)
bold = lambda size: ImageFont.truetype(str(FONTS / "font-4.ttf"), size)
scenes = json.loads((ROOT / "src/film.json").read_text())
TOTAL_DURATION = sum(scene["duration"] for scene in scenes)


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


def fade_window(local, duration, edge=.45):
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


def base_frame(scene_index, global_t):
    image = Image.new("RGBA", (W, H), WHITE + (255,))
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(H):
        ratio = y / H
        color = tuple(int(WHITE[i] * (1-ratio*.06) + PALE[i] * ratio*.06) for i in range(3))
        draw.line((0, y, W, y), fill=color + (255,))
    for x in range(64, W, 64):
        draw.line((x, 0, x, H), fill=(0, 102, 186, 10))
    for y in range(64, H, 64):
        draw.line((0, y, W, y), fill=(0, 102, 186, 10))
    draw.rectangle((0, 0, W, 7), fill=NAVY + (255,))
    draw.rectangle((0, 7, W, 10), fill=GOLD + (255,))

    start, gap = 72, 13
    segment_width = (W - start * 2 - gap * 7) / 8
    for index in range(8):
        x1 = start + index * (segment_width + gap)
        fill = NAVY if index < scene_index else MEDIUM_BLUE if index == scene_index else (207, 219, 229)
        draw.rounded_rectangle((x1, H-31, x1+segment_width, H-26), radius=3, fill=fill + (255,))
    dot_x = 80 + ((global_t * 34) % (W - 160))
    draw.ellipse((dot_x-2, 34, dot_x+2, 38), fill=LIGHT_BLUE + (100,))
    return image


def reveal(local, delay=.2, speed=.85):
    return ease((local-delay) / speed)


def text(draw, xy, value, font, fill, opacity=1, anchor=None):
    draw.text(xy, value, font=font, fill=alpha(fill, opacity), anchor=anchor)


def headline(draw, kicker, title, detail, local, x=76, y=155, width=620):
    progress = reveal(local)
    opacity = progress
    offset = int((1-progress) * 24)
    text(draw, (x, y+offset), kicker.upper(), bold(14), MEDIUM_BLUE, opacity)
    cursor = y + 50 + offset
    title_font = serif(66)
    for line in wrap(draw, title, title_font, width):
        text(draw, (x, cursor), line, title_font, NAVY, opacity)
        cursor += 64
    draw.rounded_rectangle((x, cursor+12, x+98*progress, cursor+17), radius=3, fill=alpha(GOLD, opacity))
    cursor += 42
    for line in wrap(draw, detail, regular(19), width):
        text(draw, (x, cursor), line, regular(19), GREY, opacity)
        cursor += 28


def metric(draw, amount, label, detail, local, x=78, y=195):
    progress = reveal(local)
    offset = int((1-progress) * 22)
    text(draw, (x, y+offset), label.upper(), bold(14), MEDIUM_BLUE, progress)
    text(draw, (x, y+54+offset), amount, serif(112), NAVY, progress)
    draw.rounded_rectangle((x, y+170+offset, x+110*progress, y+175+offset), radius=3, fill=alpha(GOLD, progress))
    text(draw, (x, y+202+offset), detail, regular(19), GREY, progress)


def finish(image, local, duration):
    opacity = fade_window(local, duration)
    if opacity < 1:
        image.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1-opacity)))))
    return image.convert("RGB")


def draw_node(draw, x, y, label, progress, active=False):
    radius = 45
    scale = .78 + .22 * progress
    radius = int(radius * scale)
    fill = NAVY if active else WHITE
    outline = GOLD if active else (188, 208, 224)
    draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=alpha(fill, progress), outline=alpha(outline, progress), width=3)
    if progress > .55:
        text(draw, (x, y), label, bold(12), WHITE if active else NAVY, ease((progress-.55)/.45), anchor="mm")


def opener(local, duration, global_t, index):
    image = base_frame(index, global_t)
    draw = ImageDraw.Draw(image, "RGBA")
    headline(draw, "Equal employment opportunity", "Ideas become infrastructure.", "Investment · practice · evidence · lasting opportunity", local, width=570)
    nodes = [(850, 186, "INVEST"), (1045, 286, "IMPLEMENT"), (980, 500, "MEASURE"), (770, 454, "SUSTAIN")]
    progress = reveal(local, .55, 1.1)
    for idx, (x, y, label) in enumerate(nodes):
        next_x, next_y, _ = nodes[(idx+1) % len(nodes)]
        line_progress = ease((progress-idx*.08)/.7)
        end_x = x + (next_x-x)*line_progress
        end_y = y + (next_y-y)*line_progress
        draw.line((x, y, end_x, end_y), fill=alpha(MEDIUM_BLUE, .48*progress), width=3)
        pulse = (global_t*.45 + idx/4) % 1
        px = x + (next_x-x)*pulse
        py = y + (next_y-y)*pulse
        draw.ellipse((px-5, py-5, px+5, py+5), fill=alpha(LIGHT_BLUE, progress))
    for idx, (x, y, label) in enumerate(nodes):
        draw_node(draw, x, y, label, ease((progress-idx*.07)/.8), active=idx == 0)
    return finish(image, local, duration)


def foundation(local, duration, global_t, index):
    image = base_frame(index, global_t)
    draw = ImageDraw.Draw(image, "RGBA")
    metric(draw, "$20M", "Statewide foundation · 2021", "$15.5M apportioned systemwide", local)
    progress = reveal(local, .45, 1.2)
    x1, y1, x2, y2 = 700, 260, 1170, 370
    draw.rounded_rectangle((x1, y1, x2, y2), radius=20, fill=alpha((227, 237, 245), progress))
    fill_width = (x2-x1) * .775 * progress
    draw.rounded_rectangle((x1, y1, x1+fill_width, y2), radius=20, fill=alpha(MEDIUM_BLUE, progress))
    text(draw, (x1, y1-45), "EEO BEST PRACTICES FUND", bold(14), NAVY, progress)
    text(draw, (x1+24, (y1+y2)/2), "$15.5M APPORTIONED", bold(17), WHITE, progress, anchor="lm")
    text(draw, (x2, y2+42), "77.5% of the $20M foundation", regular(16), GREY, progress, anchor="ra")
    text(draw, (700, 500), "AB 132 established a one-time statewide fund to advance equal employment opportunity practices.", regular(18), GREY, progress)
    return finish(image, local, duration)


def first_cycle(local, duration, global_t, index):
    image = base_frame(index, global_t)
    draw = ImageDraw.Draw(image, "RGBA")
    metric(draw, "$5.65M", "First competitive cycle · 2023–25", "21 district awards", local)
    start_x, start_y = 735, 185
    for item in range(21):
        row, column = divmod(item, 7)
        p = reveal(local, .35 + item*.035, .65)
        x = start_x + column*65
        y = start_y + row*98 + int((1-p)*28)
        draw.rounded_rectangle((x, y, x+48, y+64), radius=8, fill=alpha(MEDIUM_BLUE if item % 3 else NAVY, p))
        draw.ellipse((x+18, y+17, x+30, y+29), fill=alpha(WHITE, p*.95))
        draw.rounded_rectangle((x+12, y+38, x+36, y+44), radius=3, fill=alpha((182, 220, 239), p))
    text(draw, (948, 545), "21 DISTRICT AWARD SELECTIONS", bold(13), NAVY, reveal(local, 1.2), anchor="ma")
    return finish(image, local, duration)


def current_cycle(local, duration, global_t, index):
    image = base_frame(index, global_t)
    draw = ImageDraw.Draw(image, "RGBA")
    metric(draw, "$1.4M", "Current cycle · 2026–28", "11 district awards", local)
    awards = [100, 100, 100, 150, 150, 150, 100, 150, 150, 150, 100]
    start_x, baseline, chart_h = 670, 510, 285
    for item, amount in enumerate(awards):
        p = reveal(local, .42 + item*.045, .8)
        bar_h = chart_h * (amount / 150) * p
        x = start_x + item*48
        draw.rounded_rectangle((x, baseline-bar_h, x+30, baseline), radius=6, fill=alpha(NAVY if amount == 150 else MEDIUM_BLUE, p))
        if p > .75:
            text(draw, (x+15, baseline-bar_h-18), f"${amount}K", bold(10), NAVY, ease((p-.75)/.25), anchor="ma")
    for level, label in [(0, "$0"), (100, "$100K"), (150, "$150K")]:
        y = baseline-chart_h*(level/150)
        draw.line((648, y, 1204, y), fill=alpha((188, 208, 224), .7), width=1)
        text(draw, (636, y), label, regular(11), GREY, 1, anchor="ra")
    text(draw, (940, 565), "FIVE $100K AWARDS  ·  SIX $150K AWARDS", bold(12), NAVY, reveal(local, 1.4), anchor="ma")
    return finish(image, local, duration)


def combined(local, duration, global_t, index):
    image = base_frame(index, global_t)
    draw = ImageDraw.Draw(image, "RGBA")
    metric(draw, "$7.05M", "Competitive awards since launch", "32 award selections · two cycles", local)
    progress = reveal(local, .45, 1.1)
    data = [("2023–25", 5.65, "$5.65M", NAVY), ("2026–28", 1.4, "$1.4M", MEDIUM_BLUE)]
    for row, (year, value, amount, color) in enumerate(data):
        y = 260 + row*150
        text(draw, (700, y), year, bold(14), NAVY, progress)
        draw.rounded_rectangle((700, y+34, 1150, y+102), radius=12, fill=alpha((226, 236, 244), progress))
        width = 450*(value/5.65)*progress
        draw.rounded_rectangle((700, y+34, 700+width, y+102), radius=12, fill=alpha(color, progress))
        text(draw, (720, y+68), amount, bold(19), WHITE, progress, anchor="lm")
    draw.line((700, 560, 1150, 560), fill=alpha(GOLD, progress), width=4)
    text(draw, (1150, 590), "Published competitive cycles shown separately from statewide apportionment", regular(13), GREY, progress, anchor="ra")
    return finish(image, local, duration)


def districts(local, duration, global_t, index):
    image = base_frame(index, global_t)
    draw = ImageDraw.Draw(image, "RGBA")
    headline(draw, "Eleven local signals", "Awarded locally. Learned systemwide.", "Tier 1 implementation · Tier 2 LIFT mentorship", local, width=565)
    progress = reveal(local, .45, 1.1)
    center = (980, 355)
    draw.ellipse((center[0]-58, center[1]-58, center[0]+58, center[1]+58), fill=alpha(NAVY, progress))
    text(draw, center, "$1.4M", serif(32), WHITE, progress, anchor="mm")
    for item in range(11):
        angle = math.radians(-90 + item*(360/11))
        radius = 210 if item % 2 else 190
        x = center[0] + math.cos(angle)*radius
        y = center[1] + math.sin(angle)*radius
        p = ease((progress-item*.035)/.75)
        draw.line((center[0], center[1], x, y), fill=alpha(MEDIUM_BLUE, .34*p), width=2)
        is_lift = item in (1, 2, 6, 10)
        draw.ellipse((x-25, y-25, x+25, y+25), fill=alpha(MEDIUM_BLUE if is_lift else WHITE, p), outline=alpha(MEDIUM_BLUE, p), width=3)
        text(draw, (x, y), f"{item+1:02d}", bold(12), WHITE if is_lift else NAVY, p, anchor="mm")
    text(draw, (980, 605), "11 DISTRICTS  ·  7 TIER 1  ·  4 TIER 2 LIFT", bold(12), NAVY, progress, anchor="ma")
    return finish(image, local, duration)


def sustainable(local, duration, global_t, index):
    image = base_frame(index, global_t)
    draw = ImageDraw.Draw(image, "RGBA")
    headline(draw, "Sustainable impact model", "Investment that compounds.", "Projects become tested practices. Practices build shared capacity.", local, width=575)
    labels = ["INVEST", "IMPLEMENT", "LEARN", "SUSTAIN"]
    positions = [(890, 180), (1100, 330), (965, 545), (745, 395)]
    progress = reveal(local, .4, 1.0)
    for item, (x, y) in enumerate(positions):
        nx, ny = positions[(item+1) % 4]
        p = ease((progress-item*.08)/.72)
        draw.line((x, y, nx, ny), fill=alpha(MEDIUM_BLUE, .42*p), width=8)
        phase = (global_t*.35 + item*.22) % 1
        px, py = x+(nx-x)*phase, y+(ny-y)*phase
        draw.ellipse((px-7, py-7, px+7, py+7), fill=alpha(GOLD, p))
    for item, ((x, y), label) in enumerate(zip(positions, labels)):
        draw_node(draw, x, y, label, ease((progress-item*.06)/.78), active=item == 3)
    return finish(image, local, duration)


def finale(local, duration, global_t, index):
    image = base_frame(index, global_t)
    draw = ImageDraw.Draw(image, "RGBA")
    opacity = fade_window(local, duration, .35)
    assemble = ease(local / 2.15)
    starts = [(-170, 260), (640, -170), (1450, 430)]
    final_x = [510, 640, 770]
    for item, letter in enumerate("IBP"):
        p = ease((assemble-item*.08)/.84)
        x = starts[item][0] + (final_x[item]-starts[item][0])*p
        y = starts[item][1] + (310-starts[item][1])*p
        text(draw, (x, y), letter, serif(158), NAVY, opacity*p, anchor="mm")
    line = ease((local-1.45)/1.1)
    draw.rounded_rectangle((430, 425, 430+420*line, 430), radius=3, fill=alpha(GOLD, opacity))
    text(draw, (640, 476), "GRANT INITIATIVE", bold(27), NAVY, opacity*ease((local-1.8)/1.0), anchor="mm")
    text(draw, (640, 528), "IDEAS · PRACTICE · EVIDENCE · SUSTAINABLE IMPACT", bold(11), GREY, opacity*ease((local-2.6)/.9), anchor="mm")
    return finish(image, local, duration)


RENDERERS = [opener, foundation, first_cycle, current_cycle, combined, districts, sustainable, finale]


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
        image = RENDERERS[index](local, scenes[index]["duration"], current, index)
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
    print(f"Complete: {TOTAL_DURATION}s silent academic explainer", flush=True)


if __name__ == "__main__":
    main()
