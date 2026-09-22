"""No-API-key image provider: renders scene visuals and thumbnails locally
with Pillow (gradient background + bold wrapped text). It won't look like a
stock-footage production, but it lets the whole pipeline run end-to-end for
free, and it's easy to swap for an AI image provider once you have a key."""

from __future__ import annotations

import hashlib
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .base import ImageProvider

WIDTH, HEIGHT = 1280, 720

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:\\Windows\\Fonts\\arialbd.ttf",
]

_PALETTES = [
    ((16, 24, 64), (96, 32, 128)),
    ((8, 64, 56), (16, 128, 112)),
    ((80, 16, 24), (176, 48, 32)),
    ((24, 32, 16), (112, 144, 32)),
    ((48, 16, 80), (144, 32, 176)),
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for candidate in _FONT_CANDIDATES:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size=size)


def _palette_for(text: str) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return _PALETTES[digest[0] % len(_PALETTES)]


def _vertical_gradient(
    top: tuple[int, int, int], bottom: tuple[int, int, int]
) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), top)
    draw = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        color = tuple(int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
        draw.line([(0, y), (WIDTH, y)], fill=color)
    return image


def _draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_size: int,
    fill: tuple[int, int, int] = (255, 255, 255),
    max_chars_per_line: int = 22,
) -> None:
    font = _load_font(font_size)
    lines = textwrap.wrap(text, width=max_chars_per_line) or [text]
    line_height = font_size * 1.25
    total_height = line_height * len(lines)
    y = (HEIGHT - total_height) / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=4)
        line_width = bbox[2] - bbox[0]
        x = (WIDTH - line_width) / 2
        draw.text(
            (x, y),
            line,
            font=font,
            fill=fill,
            stroke_width=4,
            stroke_fill=(0, 0, 0),
        )
        y += line_height


class LocalImageProvider(ImageProvider):
    def generate_scene_image(
        self, on_screen_text: str, visual_direction: str, output_path: str
    ) -> None:
        top, bottom = _palette_for(on_screen_text or visual_direction)
        image = _vertical_gradient(top, bottom)
        draw = ImageDraw.Draw(image)
        label = on_screen_text or visual_direction
        _draw_centered_text(draw, label, font_size=64)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)

    def generate_thumbnail(self, title: str, concept: str, output_path: str) -> None:
        top, bottom = _palette_for(title)
        image = _vertical_gradient(top, bottom)
        draw = ImageDraw.Draw(image)
        _draw_centered_text(draw, title.upper(), font_size=80, max_chars_per_line=16)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)
