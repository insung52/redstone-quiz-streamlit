"""
circuit_renderer.py
레드스톤 회로 / 논리 게이트 다이어그램을 Pillow로 합성하여 PNG bytes 반환.

캐싱 전략:
  - render_circuit_image(): @st.cache_data 적용.
    Streamlit은 위젯 조작 시마다 전체 스크립트를 재실행합니다.
    이미지 합성은 스프라이트 파일 I/O + 타일 붙이기 연산을 포함하므로,
    동일한 circuit_layout에 대해 매번 재실행하면 불필요한 비용이 발생합니다.
    layout을 tuple[tuple[str]] (immutable) 로 받아 캐시 키로 사용하면
    같은 문제를 다시 볼 때 즉시 캐시에서 이미지를 반환합니다.

  - _load_sprite(): @lru_cache 적용.
    동일 스프라이트 파일을 문제마다 반복 열지 않도록 프로세스 수준 캐시.
"""

import io
import os
from functools import lru_cache

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

TILE_SIZE = 52
GRID_GAP = 3
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "sprites")

# ── 스프라이트 없을 때 사용할 플레이스홀더 색상 (RGBA) ─────────────────────
_COLORS: dict = {
    # 마인크래프트 회로
    "empty":          (45,  110,  45,  0),
    "block":          (130, 130, 130, 255),
    "wire_off":       ( 80,  10,  10, 255),
    "wire_on":        (220,  40,  40, 255),
    "torch_off":      (100,  60,  10, 255),
    "torch_on":       (255, 140,   0, 255),
    "repeater_off":   ( 70,  70, 110, 255),
    "repeater_on":    (130, 130, 255, 255),
    "lamp_off":       ( 60,  60,   0, 255),
    "lamp_on":        (255, 240,   0, 255),
    "lever_off":      (100,  70,  30, 255),
    "lever_on":       (200, 150,  50, 255),
    "comparator_off": ( 80,  40,  80, 255),
    "comparator_on":  (200, 100, 200, 255),
    # 논리 게이트
    "input_off":      ( 60,  60, 160, 255),
    "input_on":       ( 80, 160, 255, 255),
    "output_off":     ( 60, 100,  60, 255),
    "output_on":      ( 80, 220,  80, 255),
    "gate_not":       (200,  80,  80, 255),
    "gate_and":       (200, 140,  50, 255),
    "gate_or":        (160, 100, 200, 255),
    "gate_nand":      (230, 100,  60, 255),
    "gate_nor":       (180,  80, 160, 255),
    "gate_xor":       ( 80, 180, 180, 255),
    "gate_buffer":    (100, 180, 100, 255),
}

# ── 플레이스홀더에 표시할 짧은 레이블 ─────────────────────────────────────
_LABELS: dict = {
    "empty":          "",
    "block":          "BLK",
    "wire_off":       "W-",
    "wire_on":        "W+",
    "torch_off":      "T-",
    "torch_on":       "T+",
    "repeater_off":   "R-",
    "repeater_on":    "R+",
    "lamp_off":       "L-",
    "lamp_on":        "L+",
    "lever_off":      "LV-",
    "lever_on":       "LV+",
    "comparator_off": "CMP-",
    "comparator_on":  "CMP+",
    "input_off":      "IN 0",
    "input_on":       "IN 1",
    "output_off":     "OUT 0",
    "output_on":      "OUT 1",
    "gate_not":       "NOT",
    "gate_and":       "AND",
    "gate_or":        "OR",
    "gate_nand":      "NAND",
    "gate_nor":       "NOR",
    "gate_xor":       "XOR",
    "gate_buffer":    "BUF",
}


def _make_placeholder(name: str) -> Image.Image:
    """스프라이트 파일이 없을 때 색상 + 레이블로 플레이스홀더 타일 생성."""
    color = _COLORS.get(name, (100, 100, 100, 255))
    tile = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), color)

    if color[3] == 0:
        return tile  # 투명 타일 (empty)

    draw = ImageDraw.Draw(tile)
    draw.rectangle([0, 0, TILE_SIZE - 1, TILE_SIZE - 1],
                   outline=(0, 0, 0, 160), width=1)

    label = _LABELS.get(name, name[:4])
    if label:
        font = ImageFont.load_default()
        # textbbox로 텍스트 크기 측정 후 중앙 배치 (Pillow >= 8.0)
        try:
            bbox = draw.textbbox((0, 0), label, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            x = (TILE_SIZE - tw) // 2
            y = (TILE_SIZE - th) // 2
        except AttributeError:
            x, y = 4, TILE_SIZE // 2 - 5
        draw.text((x, y), label, fill=(255, 255, 255, 230), font=font)

    return tile


@lru_cache(maxsize=128)
def _load_sprite(name: str) -> Image.Image:
    """
    스프라이트 PNG 로드 (프로세스 수준 LRU 캐시).
    assets/sprites/{name}.png 가 있으면 로드, 없으면 플레이스홀더 반환.
    """
    path = os.path.join(ASSETS_DIR, f"{name}.png")
    if os.path.exists(path):
        img = Image.open(path).convert("RGBA")
        return img.resize((TILE_SIZE, TILE_SIZE), Image.NEAREST)
    return _make_placeholder(name)


@st.cache_data
def render_circuit_image(circuit_layout: tuple) -> bytes:
    """
    2D 스프라이트 배열 → Pillow 합성 → PNG bytes 반환.

    Args:
        circuit_layout: tuple[tuple[str, ...], ...] 형태의 2D 스프라이트 배열.
                        반드시 tuple(immutable)이어야 @st.cache_data 키로 사용 가능.

    Returns:
        PNG 포맷 이미지 bytes. st.image()에 직접 전달 가능.
    """
    if not circuit_layout:
        return b""

    rows = len(circuit_layout)
    cols = max(len(row) for row in circuit_layout)

    canvas_w = cols * TILE_SIZE + max(cols - 1, 0) * GRID_GAP + 8
    canvas_h = rows * TILE_SIZE + max(rows - 1, 0) * GRID_GAP + 8

    canvas = Image.new("RGBA", (canvas_w, canvas_h), (28, 28, 28, 255))

    for r, row in enumerate(circuit_layout):
        for c, name in enumerate(row):
            tile = _load_sprite(name)
            x = 4 + c * (TILE_SIZE + GRID_GAP)
            y = 4 + r * (TILE_SIZE + GRID_GAP)
            canvas.alpha_composite(tile, (x, y))

    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return buf.getvalue()
