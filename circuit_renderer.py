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


# ── 와이어 방향 인식 ────────────────────────────────────────────────────────

# 이 접두어를 가진 이웃 타일이 있으면 와이어가 그 방향으로 연결됨
# lamp 는 실제 마인크래프트 규칙상 와이어 형태 결정에 포함되지 않음
_WIRE_CONNECTABLE_PREFIXES = ("wire_", "lever_", "torch_", "repeater_")


def _neighbor(r: int, c: int, d: str) -> tuple:
    """방향 문자('N','S','E','W') → 인접 셀 좌표."""
    return {"N": (r - 1, c), "S": (r + 1, c), "E": (r, c + 1), "W": (r, c - 1)}[d]


_DIR_OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}


def _get_wire_dirs(layout: tuple, r: int, c: int) -> frozenset:
    """
    layout[r][c] 와이어 타일이 연결되는 방향 집합 반환.

    마인크래프트 규칙:
    - 이웃이 wire_* / lever_* / torch_* / repeater_* 이면 해당 방향 연결
    - 연결 방향이 1개뿐이면 반대편으로도 자동 연장 (직선)
    - 연결 방향이 0개면 십자(모든 방향)로 표시
    """
    rows = len(layout)
    dirs = set()
    for d in ("N", "S", "E", "W"):
        nr, nc = _neighbor(r, c, d)
        if 0 <= nr < rows and 0 <= nc < len(layout[nr]):
            nb = layout[nr][nc]
            if any(nb.startswith(p) for p in _WIRE_CONNECTABLE_PREFIXES):
                dirs.add(d)

    if len(dirs) == 1:
        # 한쪽만 연결 → 반대편으로도 연장해 직선으로 표시
        dirs.add(_DIR_OPPOSITE[next(iter(dirs))])
    elif len(dirs) == 0:
        # 고립된 와이어 → 십자(dot) 형태
        dirs = {"N", "S", "E", "W"}

    return frozenset(dirs)


@lru_cache(maxsize=1)
def _stone_bg() -> Image.Image:
    """돌 블록 배경 (generate_sprites.py 의 stone_bg 와 동일)."""
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (112, 112, 112, 255))
    d = ImageDraw.Draw(img)
    for x, y in [(4,4),(14,9),(7,22),(20,28),(30,6),(38,18),
                 (27,36),(41,8),(9,40),(34,40),(44,32),(16,44)]:
        d.rectangle([x, y, x + 2, y + 2], fill=(88, 88, 88, 255))
    d.rectangle([0, 0, TILE_SIZE - 1, TILE_SIZE - 1], outline=(68, 68, 68, 255), width=1)
    return img


@lru_cache(maxsize=512)
def _make_wire_tile(dirs: frozenset, on: bool, strength: int = 15) -> Image.Image:
    """
    연결 방향·신호 유무·강도에 맞는 와이어 타일 동적 생성 (LRU 캐시).
    dirs   : frozenset({'N','S','E','W'}) — 연결 방향
    on     : 신호 있음 여부
    strength: 신호 강도 1-15 (on=True 일 때만 의미 있음)
    """
    H = TILE_SIZE // 2
    img = _stone_bg().copy()          # 캐시된 배경을 복사해 사용
    draw = ImageDraw.Draw(img)

    if on:
        t = 0.2 + 0.8 * (strength / 15)
        outer  = (int(210 * t), int(35 * t), int(35 * t), 255)
        inner  = (int(255 * t), int(100 * t), int(100 * t), 255)
        lw     = max(2, round(2 + 3 * t))
        dot_r  = max(2, round(2 + 3 * t))
    else:
        outer  = (85, 12, 12, 255)
        inner  = (105, 18, 18, 255)
        lw     = 3
        dot_r  = 3

    # 연결된 방향으로만 선 그리기
    if "W" in dirs: draw.line([(0, H), (H, H)],            fill=outer, width=lw)
    if "E" in dirs: draw.line([(H, H), (TILE_SIZE, H)],    fill=outer, width=lw)
    if "N" in dirs: draw.line([(H, 0), (H, H)],            fill=outer, width=lw)
    if "S" in dirs: draw.line([(H, H), (H, TILE_SIZE)],    fill=outer, width=lw)

    # 중심 점 (항상 표시)
    draw.ellipse([H - dot_r, H - dot_r, H + dot_r, H + dot_r], fill=inner)

    # ON 상태 — 우측 하단에 신호 강도 숫자 (흰색 + 검은 외곽선)
    if on:
        label = str(strength)
        font  = ImageFont.load_default()
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            draw.text((TILE_SIZE - 14 + dx, TILE_SIZE - 12 + dy),
                      label, fill=(0, 0, 0, 200), font=font)
        draw.text((TILE_SIZE - 14, TILE_SIZE - 12),
                  label, fill=(255, 255, 255, 255), font=font)

    return img


# 퀴즈 중 모든 ON 상태를 OFF로 교체 (입력인 lever/input 제외)
_QUIZ_MASK = {
    "wire_on":        "wire_off",
    "torch_on":       "torch_off",
    "repeater_on":    "repeater_off",
    "lamp_on":        "lamp_off",
    "input_on":       "input_off",
    "conn_on":        "conn_off",
    "output_on":      "output_off",
    "comparator_on":  "comparator_off",
}


def mask_answers(layout: tuple) -> tuple:
    """
    퀴즈 페이지용: lever/input(입력 조건) 제외하고
    모든 ON 스프라이트를 OFF로 교체.
    결과 페이지에서는 원본 layout을 그대로 사용.
    """
    return tuple(
        tuple(_QUIZ_MASK.get(cell, cell) for cell in row)
        for row in layout
    )


# 애니메이션에서 순차 활성화할 ON 스프라이트 목록
_ON_SPRITES = frozenset({
    "lever_on", "wire_on", "torch_on", "repeater_on", "lamp_on",
    "comparator_on", "input_on", "conn_on", "output_on",
})


# 신호 동작 분류
_SIGNAL_SOURCES   = frozenset({"lever_on", "torch_on", "input_on"})  # 강도 15 방출
_SIGNAL_RESETTERS = frozenset({"repeater_on"})                        # 강도 15 재설정
_SIGNAL_WIRES     = frozenset({"wire_on", "conn_on"})                 # 강도 1씩 감소


def _bfs_signal_order(layout: tuple) -> list:
    """
    소스(lever_on, torch_on, input_on)에서 BFS로 신호 전파 순서 계산.
    리피터는 출력 방향(오른쪽)으로만 신호를 전파 (현재 레이아웃 기준 우향 고정).
    반환: [(r, c, name), ...] — 활성화 순서
    """
    on_tiles = {
        (r, c): name
        for r, row in enumerate(layout)
        for c, name in enumerate(row)
        if name in _ON_SPRITES
    }
    if not on_tiles:
        return []

    # 소스 타일에서 BFS 시작
    sources = [(r, c) for (r, c), nm in on_tiles.items() if nm in _SIGNAL_SOURCES]
    if not sources:
        sources = [min(on_tiles.keys())]

    visited: dict = {}
    queue: list = []
    for pos in sources:
        if pos not in visited:
            visited[pos] = len(visited)
            queue.append(pos)

    head = 0
    while head < len(queue):
        r, c = queue[head]; head += 1
        name = on_tiles[(r, c)]

        # 리피터(우향)는 E 방향으로만 전파
        dirs = ("E",) if name in _SIGNAL_RESETTERS else ("N", "S", "E", "W")
        for d in dirs:
            nr, nc = _neighbor(r, c, d)
            if (nr, nc) in on_tiles and (nr, nc) not in visited:
                visited[(nr, nc)] = len(visited)
                queue.append((nr, nc))

    # BFS에서 방문 못한 ON 타일은 뒤에 추가
    ordered = sorted(on_tiles.keys(), key=lambda p: visited.get(p, 9999))
    return [(r, c, on_tiles[(r, c)]) for r, c in ordered]


def compute_signal_strengths(circuit_layout: tuple) -> dict:
    """
    BFS 신호 전파 순서 기반으로 각 ON 타일의 신호 강도 계산.
    큐에 (r, c, incoming_strength)를 함께 저장해 분기 시에도 각 경로가
    독립적으로 강도를 계산하도록 한다 (공유 counter 방식의 분기 오류 수정).
    반환: {(row, col): strength}
    """
    on_tiles = {
        (r, c): name
        for r, row in enumerate(circuit_layout)
        for c, name in enumerate(row)
        if name in _ON_SPRITES
    }
    if not on_tiles:
        return {}

    strengths: dict = {}
    visited: set = set()

    # 큐 항목: (r, c, incoming_strength)
    queue: list = []
    for (r, c), name in on_tiles.items():
        if name in _SIGNAL_SOURCES:
            queue.append((r, c, 15))

    if not queue:
        queue = [(r, c, 15) for (r, c) in [min(on_tiles.keys())]]

    head = 0
    while head < len(queue):
        r, c, incoming = queue[head]
        head += 1

        if (r, c) in visited:
            continue
        visited.add((r, c))

        name = on_tiles.get((r, c))
        if name is None:
            continue

        if name in _SIGNAL_SOURCES:
            my_strength = 15
            out_strength = 15   # 소스 이웃 와이어는 15를 받음
        elif name in _SIGNAL_RESETTERS:
            my_strength = 15
            out_strength = 15   # 리피터 출력은 항상 15
        elif name in _SIGNAL_WIRES:
            my_strength = incoming
            out_strength = max(0, incoming - 1)
        else:
            my_strength = incoming
            out_strength = max(0, incoming - 1)

        strengths[(r, c)] = my_strength

        # 리피터는 동쪽(E)으로만 신호 전파
        dirs = ("E",) if name in _SIGNAL_RESETTERS else ("N", "S", "E", "W")
        for d in dirs:
            nr, nc = _neighbor(r, c, d)
            if (nr, nc) in on_tiles and (nr, nc) not in visited:
                queue.append((nr, nc, out_strength))

    return strengths


def get_animation_frames(circuit_layout: tuple) -> list:
    """
    BFS 순서로 타일을 하나씩 활성화하는 애니메이션 프레임 목록 반환.
    반환: [(frame_layout, signal_strengths_dict), ...]
    """
    on_positions = _bfs_signal_order(circuit_layout)
    pre_strengths = compute_signal_strengths(circuit_layout)

    frames = [(mask_answers(circuit_layout), {})]  # 초기: 전체 꺼짐

    for i in range(1, len(on_positions) + 1):
        active     = on_positions[:i]
        active_set = {(r, c) for r, c, _ in active}
        sig        = {(r, c): pre_strengths[(r, c)] for r, c, _ in active}
        frame_layout = tuple(
            tuple(
                name if (r, c) in active_set else _QUIZ_MASK.get(name, name)
                for c, name in enumerate(row)
            )
            for r, row in enumerate(circuit_layout)
        )
        frames.append((frame_layout, sig))

    return frames


def _render_canvas(circuit_layout: tuple, signal_strengths: dict | None) -> bytes:
    """
    공통 렌더 헬퍼.
    signal_strengths 가 None 이면 와이어를 단순 on/off(강도 15)로 렌더.
    signal_strengths 가 있으면 해당 강도로 렌더 (애니메이션·정답 표시용).
    """
    if not circuit_layout:
        return b""

    rows = len(circuit_layout)
    cols = max(len(row) for row in circuit_layout)
    canvas_w = cols * TILE_SIZE + max(cols - 1, 0) * GRID_GAP + 8
    canvas_h = rows * TILE_SIZE + max(rows - 1, 0) * GRID_GAP + 8
    canvas   = Image.new("RGBA", (canvas_w, canvas_h), (28, 28, 28, 255))

    for r, row in enumerate(circuit_layout):
        for c, name in enumerate(row):
            if name.startswith("wire_"):
                dirs = _get_wire_dirs(circuit_layout, r, c)
                on   = (name != "wire_off")
                if signal_strengths is not None:
                    s = signal_strengths.get((r, c), 15 if on else 0)
                    on = on and s > 0
                    tile = _make_wire_tile(dirs, on, max(1, s) if on else 15)
                else:
                    tile = _make_wire_tile(dirs, on, 15)
            else:
                tile = _load_sprite(name)
            x = 4 + c * (TILE_SIZE + GRID_GAP)
            y = 4 + r * (TILE_SIZE + GRID_GAP)
            canvas.alpha_composite(tile, (x, y))

    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return buf.getvalue()


@st.cache_data
def render_circuit_image(circuit_layout: tuple) -> bytes:
    """
    2D 스프라이트 배열 → PNG bytes (캐시됨).
    와이어 형태는 이웃 타일 기반으로 자동 결정.
    신호 강도 표시 없음 (퀴즈 마스킹·결과 미리보기용).
    """
    return _render_canvas(circuit_layout, None)


def render_circuit_frame(circuit_layout: tuple, signal_strengths: dict) -> bytes:
    """
    애니메이션 프레임 렌더링 (캐시 없음).
    signal_strengths: {(row, col): strength} — 와이어에 강도 색상·숫자 적용.
    """
    return _render_canvas(circuit_layout, signal_strengths)
