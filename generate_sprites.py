"""
generate_sprites.py
assets/sprites/ 폴더에 퀴즈용 스프라이트 PNG를 생성합니다.
마인크래프트 공식 텍스처를 일절 사용하지 않는 오리지널 픽셀아트입니다.

실행: python generate_sprites.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

SIZE = 52
H = SIZE // 2
OUT = os.path.join(os.path.dirname(__file__), "assets", "sprites")
os.makedirs(OUT, exist_ok=True)

font = ImageFont.load_default()


def save(img: Image.Image, name: str) -> None:
    img.save(os.path.join(OUT, f"{name}.png"))
    print(f"  생성: {name}.png")


def draw_text_centered(d: ImageDraw.ImageDraw, text: str, cx: int, cy: int,
                       fill=(255, 255, 255, 255)) -> None:
    try:
        bbox = d.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        d.text((cx - tw // 2, cy - th // 2), text, fill=fill, font=font)
    except AttributeError:
        d.text((cx - len(text) * 3, cy - 5), text, fill=fill, font=font)


# ══════════════════════════════════════════════════════════════════════════════
# 배경 헬퍼
# ══════════════════════════════════════════════════════════════════════════════

def stone_bg() -> Image.Image:
    """회색 돌 블록 스타일 배경."""
    img = Image.new("RGBA", (SIZE, SIZE), (112, 112, 112, 255))
    d = ImageDraw.Draw(img)
    texture_spots = [
        (4, 4), (14, 9), (7, 22), (20, 28),
        (30, 6), (38, 18), (27, 36), (41, 8),
        (9, 40), (34, 40), (44, 32), (16, 44),
    ]
    for x, y in texture_spots:
        d.rectangle([x, y, x + 2, y + 2], fill=(88, 88, 88, 255))
    d.rectangle([0, 0, SIZE - 1, SIZE - 1], outline=(68, 68, 68, 255), width=1)
    return img


def gate_bg(tint=(240, 240, 248, 255)) -> Image.Image:
    """논리 게이트용 밝은 배경."""
    img = Image.new("RGBA", (SIZE, SIZE), tint)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, SIZE - 1, SIZE - 1], outline=(180, 180, 200, 255), width=1)
    return img


# ══════════════════════════════════════════════════════════════════════════════
# 마인크래프트 스프라이트
# ══════════════════════════════════════════════════════════════════════════════

def gen_empty():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    save(img, "empty")


def gen_block():
    img = stone_bg()
    d = ImageDraw.Draw(img)
    # 진한 테두리 이중선으로 '블록' 느낌
    d.rectangle([2, 2, SIZE - 3, SIZE - 3], outline=(55, 55, 55, 255), width=2)
    d.rectangle([5, 5, SIZE - 6, SIZE - 6], outline=(75, 75, 75, 255), width=1)
    save(img, "block")


def gen_wire(on: bool):
    img = stone_bg()
    d = ImageDraw.Draw(img)
    if on:
        outer = (210, 35, 35, 255)
        inner = (255, 100, 100, 255)
        w = 5
    else:
        outer = (85, 12, 12, 255)
        inner = (105, 18, 18, 255)
        w = 3
    # 십자 와이어
    d.line([(3, H), (SIZE - 3, H)], fill=outer, width=w)
    d.line([(H, 3), (H, SIZE - 3)], fill=outer, width=w)
    # 중심 점
    r = 5 if on else 3
    d.ellipse([H - r, H - r, H + r, H + r], fill=inner)
    name = "wire_on" if on else "wire_off"
    save(img, name)


def gen_torch(on: bool):
    img = stone_bg()
    d = ImageDraw.Draw(img)
    cx = H
    stick_color = (140, 90, 40, 255)
    # 막대
    d.rectangle([cx - 2, H + 2, cx + 2, SIZE - 5], fill=stick_color)
    if on:
        # 불꽃 (주황 → 노란 코어)
        d.ellipse([cx - 5, 7, cx + 5, 20], fill=(255, 130, 0, 255))
        d.ellipse([cx - 3, 9, cx + 3, 17], fill=(255, 220, 50, 255))
        # 막대 상단 연결
        d.rectangle([cx - 2, 17, cx + 2, H + 4], fill=stick_color)
    else:
        # 꺼진 심지 (어두운 갈색)
        d.rectangle([cx - 2, 12, cx + 2, H + 4], fill=stick_color)
        d.ellipse([cx - 4, 8, cx + 4, 16], fill=(65, 42, 18, 255))
    name = "torch_on" if on else "torch_off"
    save(img, name)


def gen_repeater(on: bool):
    img = stone_bg()
    d = ImageDraw.Draw(img)
    # 슬랩 본체
    d.rectangle([3, H - 7, SIZE - 3, H + 8], fill=(128, 128, 128, 255))
    d.rectangle([3, H - 7, SIZE - 3, H + 8], outline=(78, 78, 78, 255), width=1)

    back_x = SIZE // 4

    # 뒤쪽 횃불: on이면 켜짐
    if on:
        d.rectangle([back_x - 2, H - 17, back_x + 2, H - 6], fill=(140, 90, 40, 255))
        d.ellipse([back_x - 4, H - 22, back_x + 4, H - 14], fill=(255, 130, 0, 255))
        d.ellipse([back_x - 2, H - 20, back_x + 2, H - 15], fill=(255, 220, 50, 255))
    else:
        d.rectangle([back_x - 2, H - 16, back_x + 2, H - 6], fill=(90, 58, 25, 255))
        d.ellipse([back_x - 3, H - 20, back_x + 3, H - 13], fill=(60, 38, 15, 255))

    # 앞쪽 횃불: 항상 꺼짐
    front_x = SIZE * 3 // 4
    d.rectangle([front_x - 2, H - 14, front_x + 2, H - 6], fill=(90, 58, 25, 255))
    d.ellipse([front_x - 3, H - 17, front_x + 3, H - 11], fill=(60, 38, 15, 255))

    # 방향 화살표 →
    ax = SIZE - 9
    d.polygon([(ax - 5, H - 4), (ax + 3, H), (ax - 5, H + 4)],
              fill=(200, 200, 200, 255))

    name = "repeater_on" if on else "repeater_off"
    save(img, name)


def gen_lamp(on: bool):
    if on:
        bg_color = (215, 195, 45, 255)
        line_color = (170, 150, 25, 255)
        glow_color = (255, 245, 160, 180)
    else:
        bg_color = (65, 55, 8, 255)
        line_color = (45, 38, 5, 255)
        glow_color = None

    img = Image.new("RGBA", (SIZE, SIZE), bg_color)
    d = ImageDraw.Draw(img)

    # 글로우스톤 격자 패턴
    for x in range(0, SIZE, SIZE // 3):
        d.line([(x, 0), (x, SIZE)], fill=line_color, width=1)
    for y in range(0, SIZE, SIZE // 3):
        d.line([(0, y), (SIZE, y)], fill=line_color, width=1)

    if on:
        # 중앙 발광 원
        d.ellipse([H - 11, H - 11, H + 11, H + 11], fill=glow_color)

    d.rectangle([0, 0, SIZE - 1, SIZE - 1], outline=(38, 32, 3, 255), width=1)
    name = "lamp_on" if on else "lamp_off"
    save(img, name)


def gen_lever(on: bool):
    img = stone_bg()
    d = ImageDraw.Draw(img)
    # 받침대
    d.rectangle([H - 8, H + 6, H + 8, SIZE - 4], fill=(98, 98, 98, 255))
    d.rectangle([H - 8, H + 6, H + 8, SIZE - 4], outline=(58, 58, 58, 255), width=1)
    stick = (135, 88, 42, 255)
    knob = (165, 110, 55, 255)
    if on:
        # 오른쪽 위로 기울어짐
        d.line([(H, H + 6), (H + 11, H - 9)], fill=stick, width=4)
        d.ellipse([H + 7, H - 14, H + 15, H - 6], fill=knob)
    else:
        # 왼쪽 위로 기울어짐
        d.line([(H, H + 6), (H - 11, H - 9)], fill=stick, width=4)
        d.ellipse([H - 15, H - 14, H - 7, H - 6], fill=(100, 65, 28, 255))
    name = "lever_on" if on else "lever_off"
    save(img, name)


# ══════════════════════════════════════════════════════════════════════════════
# 논리 게이트 스프라이트
# ══════════════════════════════════════════════════════════════════════════════

def gen_input(on: bool):
    color = (55, 140, 255, 255) if on else (55, 75, 155, 255)
    img = Image.new("RGBA", (SIZE, SIZE), color)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, SIZE - 1, SIZE - 1], outline=(25, 45, 120, 255), width=2)
    # 큰 0/1
    value = "1" if on else "0"
    draw_text_centered(d, value, H, H - 4)
    draw_text_centered(d, "IN", H, SIZE - 10, fill=(255, 255, 255, 170))
    name = "input_on" if on else "input_off"
    save(img, name)


def gen_output(on: bool):
    color = (45, 175, 75, 255) if on else (28, 85, 38, 255)
    img = Image.new("RGBA", (SIZE, SIZE), color)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, SIZE - 1, SIZE - 1], outline=(15, 55, 20, 255), width=2)
    value = "1" if on else "0"
    draw_text_centered(d, value, H, H - 4)
    draw_text_centered(d, "OUT", H, SIZE - 10, fill=(255, 255, 255, 170))
    name = "output_on" if on else "output_off"
    save(img, name)


def gen_gate_not():
    """NOT 게이트: 삼각형 + 끝에 작은 원."""
    img = gate_bg((255, 238, 238, 255))
    d = ImageDraw.Draw(img)
    lx, rx = 7, 36
    body_color = (200, 75, 75, 255)
    line_color = (140, 35, 35, 255)
    # 삼각형
    d.polygon([(lx, 9), (rx, H), (lx, SIZE - 9)],
              fill=body_color, outline=line_color)
    # 출력 원
    d.ellipse([rx, H - 5, rx + 10, H + 5], fill=body_color, outline=line_color)
    # 입력 선
    d.line([(0, H), (lx, H)], fill=line_color, width=2)
    # 출력 선
    d.line([(rx + 10, H), (SIZE, H)], fill=line_color, width=2)
    save(img, "gate_not")


def gen_gate_and():
    """AND 게이트: 왼쪽 평면 + 오른쪽 반원 D자."""
    img = gate_bg((255, 245, 228, 255))
    d = ImageDraw.Draw(img)
    lx = 8
    body_color = (200, 138, 48, 255)
    line_color = (138, 88, 18, 255)
    top, bot = 9, SIZE - 9

    # 왼쪽 사각형 절반
    mid_x = H + 2
    d.rectangle([lx, top, mid_x, bot], fill=body_color)
    # 오른쪽 반원
    d.pieslice([mid_x - (bot - top) // 2, top,
                mid_x + (bot - top) // 2, bot],
               start=-90, end=90, fill=body_color)
    # 윤곽
    d.line([(lx, top), (lx, bot)], fill=line_color, width=2)
    d.line([(lx, top), (mid_x, top)], fill=line_color, width=2)
    d.line([(lx, bot), (mid_x, bot)], fill=line_color, width=2)
    # 입력 선 2개
    d.line([(0, H - 8), (lx, H - 8)], fill=line_color, width=2)
    d.line([(0, H + 8), (lx, H + 8)], fill=line_color, width=2)
    # 출력 선
    out_x = mid_x + (bot - top) // 2
    d.line([(out_x, H), (SIZE, H)], fill=line_color, width=2)
    save(img, "gate_and")


def gen_gate_or():
    """OR 게이트: 방패/총알 모양 폴리곤."""
    img = gate_bg((245, 235, 255, 255))
    d = ImageDraw.Draw(img)
    body_color = (158, 98, 210, 255)
    line_color = (98, 48, 155, 255)
    # 몸통: 왼쪽 오목한 곡선 + 오른쪽 뾰족한 끝
    pts = [
        (6, 9),
        (28, 9),
        (SIZE - 5, H),
        (28, SIZE - 9),
        (6, SIZE - 9),
        (15, H),
    ]
    d.polygon(pts, fill=body_color, outline=line_color)
    # 입력 선 2개 (왼쪽 오목 곡선 위/아래 맞춤)
    d.line([(0, H - 8), (11, H - 8)], fill=line_color, width=2)
    d.line([(0, H + 8), (11, H + 8)], fill=line_color, width=2)
    # 출력 선
    d.line([(SIZE - 5, H), (SIZE, H)], fill=line_color, width=2)
    save(img, "gate_or")


def gen_gate_buffer():
    """버퍼(BUF) 게이트: 오른쪽을 향한 삼각형."""
    img = gate_bg((235, 255, 235, 255))
    d = ImageDraw.Draw(img)
    lx, rx = 7, SIZE - 7
    body_color = (75, 175, 75, 255)
    line_color = (38, 118, 38, 255)
    d.polygon([(lx, 9), (rx, H), (lx, SIZE - 9)],
              fill=body_color, outline=line_color)
    d.line([(0, H), (lx, H)], fill=line_color, width=2)
    d.line([(rx, H), (SIZE, H)], fill=line_color, width=2)
    save(img, "gate_buffer")


def gen_conn(on: bool):
    """논리 회로 전용 연결선. wire_on/off 대신 logic_layout에서 사용."""
    img = gate_bg()
    d = ImageDraw.Draw(img)
    color = (55, 140, 255, 255) if on else (160, 160, 175, 255)
    width = 3
    d.line([(0, H), (SIZE, H)], fill=color, width=width)
    # 중심 작은 점
    r = 3
    d.ellipse([H - r, H - r, H + r, H + r], fill=color)
    name = "conn_on" if on else "conn_off"
    save(img, name)


def gen_wire_strength(strength: int):
    """와이어 신호 강도별 스프라이트 (wire_on_1 ~ wire_on_15).
    강도 15 = 최대 밝기, 1 = 최소 밝기(어두운 빨강). 우측 하단에 강도 숫자 표시.
    """
    img = stone_bg()
    d = ImageDraw.Draw(img)
    t = 0.2 + 0.8 * (strength / 15)
    outer = (int(210 * t), int(35 * t), int(35 * t), 255)
    inner = (int(255 * t), int(100 * t), int(100 * t), 255)
    w = max(2, round(2 + 3 * (strength / 15)))
    d.line([(3, H), (SIZE - 3, H)], fill=outer, width=w)
    d.line([(H, 3), (H, SIZE - 3)], fill=outer, width=w)
    r = max(2, round(2 + 3 * (strength / 15)))
    d.ellipse([H - r, H - r, H + r, H + r], fill=inner)
    # 강도 숫자 (우측 하단, 흰색 테두리 효과)
    label = str(strength)
    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        d.text((SIZE - 14 + dx, SIZE - 12 + dy), label, fill=(0, 0, 0, 200), font=font)
    d.text((SIZE - 14, SIZE - 12), label, fill=(255, 255, 255, 255), font=font)
    save(img, f"wire_on_{strength}")


def gen_conn_strength(strength: int):
    """논리 커넥터 신호 강도별 스프라이트 (conn_on_1 ~ conn_on_15). 우측 하단에 강도 숫자 표시."""
    img = gate_bg()
    d = ImageDraw.Draw(img)
    t = 0.2 + 0.8 * (strength / 15)
    color = (int(55 * t), int(140 * t), int(255 * t), 255)
    w = max(1, round(1 + 2 * (strength / 15)))
    d.line([(0, H), (SIZE, H)], fill=color, width=w)
    r = max(1, round(1 + 2 * (strength / 15)))
    d.ellipse([H - r, H - r, H + r, H + r], fill=color)
    label = str(strength)
    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        d.text((SIZE - 14 + dx, SIZE - 12 + dy), label, fill=(0, 0, 0, 200), font=font)
    d.text((SIZE - 14, SIZE - 12), label, fill=(255, 255, 255, 255), font=font)
    save(img, f"conn_on_{strength}")


# ══════════════════════════════════════════════════════════════════════════════
# 실행
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"스프라이트 생성 중 → {OUT}\n")

    # 마인크래프트 회로 스프라이트
    gen_empty()
    gen_block()
    gen_wire(on=False)
    gen_wire(on=True)
    gen_torch(on=False)
    gen_torch(on=True)
    gen_repeater(on=False)
    gen_repeater(on=True)
    gen_lamp(on=False)
    gen_lamp(on=True)
    gen_lever(on=False)
    gen_lever(on=True)

    # 논리 게이트 스프라이트
    gen_input(on=False)
    gen_input(on=True)
    gen_output(on=False)
    gen_output(on=True)
    gen_gate_not()
    gen_gate_and()
    gen_gate_or()
    gen_gate_buffer()
    gen_conn(on=False)
    gen_conn(on=True)

    # 신호 강도별 와이어/커넥터 (애니메이션용)
    for s in range(1, 16):
        gen_wire_strength(s)
    for s in range(1, 16):
        gen_conn_strength(s)

    total = 22 + 15 + 15
    print(f"\n완료! 총 {total}개 파일이 생성되었습니다.")
    print("이제 'python -m streamlit run app.py' 로 앱을 실행하세요.")
