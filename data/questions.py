import streamlit as st


@st.cache_data
def load_questions(level: str = "basic") -> list:
    """
    퀴즈 문항 로드.

    캐싱 이유: 문항 데이터는 앱 실행 중 변하지 않습니다.
    Streamlit은 위젯 조작 시마다 스크립트를 재실행하므로,
    @st.cache_data 없이는 라디오 버튼 클릭마다 리스트를 재생성합니다.
    캐싱으로 최초 1회만 생성하고 이후에는 캐시에서 즉시 반환합니다.

    level: "basic" | "advanced"
    circuit_layout: 마인크래프트 회로 스프라이트 2D 튜플
    logic_layout:   논리 게이트 다이어그램 스프라이트 2D 튜플
    두 layout 모두 circuit_renderer.render_circuit_image()로 렌더링됩니다.
    """
    all_questions = [
        # ══════════════════════════════════════════════════════════════════════
        # 기초 레벨 (Q1–Q10)
        # ══════════════════════════════════════════════════════════════════════

        # ── Q1 ── 기본 회로 (켜짐) ─────────────────────────────────────────
        {
            "id": 1,
            "level": "basic",
            "title": "기본 레드스톤 회로",
            "description": (
                "레드스톤 와이어로 연결된 간단한 회로입니다. "
                "이 회로에서 레버를 켜면 램프의 상태는?"
            ),
            "circuit_layout": (
                ("lever_on", "wire_on", "wire_on", "wire_on", "lamp_on"),
            ),
            "logic_layout": (
                ("input_on", "conn_on", "conn_on", "conn_on", "output_on"),
            ),
            "choices": ["켜짐 (ON)", "꺼짐 (OFF)", "깜빡임", "신호 없음"],
            "answer_index": 0,
            "explanation": (
                "레버(입력 1)가 켜지면 레드스톤 신호가 와이어를 따라 흐르고 램프가 켜집니다. "
                "논리적으로 입력이 1이면 출력도 1인 단순 연결 회로입니다."
            ),
            "difficulty": "easy",
            "topic": "basic",
        },
        # ── Q2 ── 기본 회로 (꺼짐) ─────────────────────────────────────────
        {
            "id": 2,
            "level": "basic",
            "title": "꺼진 레버",
            "description": (
                "Q1과 동일한 구조의 회로입니다. "
                "이 회로에서 레버를 끄면 램프의 상태는?"
            ),
            "circuit_layout": (
                ("lever_off", "wire_off", "wire_off", "wire_off", "lamp_off"),
            ),
            "logic_layout": (
                ("input_off", "conn_off", "conn_off", "conn_off", "output_off"),
            ),
            "choices": ["켜짐 (ON)", "꺼짐 (OFF)", "깜빡임", "신호 없음"],
            "answer_index": 1,
            "explanation": (
                "레버(입력 0)가 꺼지면 신호가 없으므로 와이어에 신호가 흐르지 않고 램프도 꺼집니다. "
                "입력 0 → 출력 0."
            ),
            "difficulty": "easy",
            "topic": "basic",
        },
        # ── Q3 ── 리피터 통과 ──────────────────────────────────────────────
        {
            "id": 3,
            "level": "basic",
            "title": "리피터 통과",
            "description": (
                "레버와 램프 사이 중간에 **리피터**가 배치된 회로입니다. "
                "이 회로에서 레버를 켜면 램프의 상태는?"
            ),
            "circuit_layout": (
                ("lever_on", "wire_on", "repeater_on", "wire_on", "lamp_on"),
            ),
            "logic_layout": (
                ("input_on", "conn_on", "gate_buffer", "conn_on", "output_on"),
            ),
            "choices": [
                "켜짐 (ON)",
                "꺼짐 (OFF)",
                "리피터에서 신호 차단됨",
                "깜빡임",
            ],
            "answer_index": 0,
            "explanation": (
                "리피터(버퍼 게이트)는 신호를 받아 강도를 15로 갱신하여 그대로 전달합니다. "
                "입력 1 → 버퍼 → 출력 1."
            ),
            "difficulty": "easy",
            "topic": "repeater",
        },
        # ── Q4 ── NOT 게이트 (입력 꺼짐) ──────────────────────────────────
        {
            "id": 4,
            "level": "basic",
            "title": "NOT 게이트 — 꺼진 입력",
            "description": (
                "블록 오른쪽 면에 횃불이 부착된 NOT 게이트 회로입니다. "
                "이 회로에서 레버를 끄면 램프의 상태는?\n\n"
                "> 횃불은 블록이 신호를 받지 않을 때 켜집니다."
            ),
            "circuit_layout": (
                ("lever_off", "wire_off", "block", "torch_on", "lamp_on"),
            ),
            "logic_layout": (
                ("input_off", "conn_off", "gate_not", "output_on"),
            ),
            "choices": ["켜짐 (ON)", "꺼짐 (OFF)", "깜빡임", "알 수 없음"],
            "answer_index": 0,
            "explanation": (
                "NOT 게이트는 입력을 반전합니다. "
                "레버 꺼짐(0) → 블록 비활성 → 횃불 켜짐 → 램프 켜짐(1). "
                "논리식: 출력 = NOT(입력) = NOT(0) = 1."
            ),
            "difficulty": "medium",
            "topic": "not_gate",
        },
        # ── Q5 ── NOT 게이트 (입력 켜짐) ──────────────────────────────────
        {
            "id": 5,
            "level": "basic",
            "title": "NOT 게이트 — 켜진 입력",
            "description": (
                "Q4와 동일한 NOT 게이트 회로입니다. "
                "이번엔 레버를 켜면 램프의 상태는?\n\n"
                "> 횃불은 블록이 신호를 받으면 꺼집니다."
            ),
            "circuit_layout": (
                ("lever_on", "wire_on", "block", "torch_off", "lamp_off"),
            ),
            "logic_layout": (
                ("input_on", "conn_on", "gate_not", "output_off"),
            ),
            "choices": ["켜짐 (ON)", "꺼짐 (OFF)", "깜빡임", "알 수 없음"],
            "answer_index": 1,
            "explanation": (
                "레버 켜짐(1) → 와이어 → 블록 활성화 → 블록 측면 횃불 꺼짐 → 램프 꺼짐(0). "
                "논리식: 출력 = NOT(1) = 0."
            ),
            "difficulty": "medium",
            "topic": "not_gate",
        },
        # ── Q6 ── 리피터 단방향 ────────────────────────────────────────────
        {
            "id": 6,
            "level": "basic",
            "title": "리피터의 방향성",
            "description": (
                "리피터가 **오른쪽(→)** 방향으로 설치된 회로입니다. "
                "레버는 오른쪽, 램프는 왼쪽에 있습니다. "
                "레버를 켜면 램프의 상태는?\n\n"
                "> 리피터는 신호를 한 방향으로만 통과시킵니다."
            ),
            "circuit_layout": (
                ("lamp_off", "wire_off", "repeater_off", "wire_on", "lever_on"),
            ),
            "logic_layout": (
                ("output_off", "conn_off", "gate_buffer", "conn_on", "input_on"),
            ),
            "choices": [
                "켜짐 (ON)",
                "꺼짐 (OFF)",
                "깜빡임",
                "리피터 방향에 무관하게 켜짐",
            ],
            "answer_index": 1,
            "explanation": (
                "리피터(버퍼)는 단방향 소자입니다. "
                "신호 흐름 방향(오른→왼)이 리피터 방향(왼→오른)과 반대이므로 신호가 차단됩니다. "
                "논리 회로에서도 버퍼는 입력→출력 방향만 허용합니다."
            ),
            "difficulty": "medium",
            "topic": "repeater",
        },
        # ── Q7 ── 이중 NOT (버퍼) ─────────────────────────────────────────
        {
            "id": 7,
            "level": "basic",
            "title": "이중 NOT 게이트 (버퍼)",
            "description": (
                "NOT 게이트 두 개가 직렬로 연결된 회로입니다. "
                "레버를 켜면 최종 램프의 상태는?"
            ),
            "circuit_layout": (
                ("lever_on", "wire_on", "block", "torch_off", "wire_off", "block", "torch_on", "lamp_on"),
            ),
            "logic_layout": (
                ("input_on", "conn_on", "gate_not", "conn_off", "gate_not", "output_on"),
            ),
            "choices": ["켜짐 (ON)", "꺼짐 (OFF)", "깜빡임", "알 수 없음"],
            "answer_index": 0,
            "explanation": (
                "NOT(NOT(x)) = x. "
                "1단계 NOT: 입력 1 → 출력 0. "
                "2단계 NOT: 입력 0 → 출력 1. "
                "최종 출력은 원래 입력과 같습니다. 이를 버퍼(동일 출력) 회로라 합니다."
            ),
            "difficulty": "medium",
            "topic": "not_gate",
        },
        # ── Q8 ── 신호 강도 한계 (S자 16블록) ───────────────────────────────
        {
            "id": 8,
            "level": "basic",
            "title": "신호 강도 한계",
            "description": (
                "레드스톤 신호는 최대 강도 **15**이며, 1블록 이동마다 1씩 감소합니다. "
                "레버에서 **16블록** 떨어진 맨 끝 와이어의 신호 강도는?\n\n"
                "> 회로가 S자로 꺾여 있습니다. 위 행이 오른쪽으로, 아래 행이 왼쪽으로 이어집니다."
            ),
            "circuit_layout": (
                ("lever_on", "wire_on", "wire_on", "wire_on", "wire_on",
                             "wire_on", "wire_on", "wire_on", "wire_on"),
                ("empty",    "empty",   "empty",   "empty",   "empty",
                             "empty",   "empty",   "empty",   "wire_on"),
                ("empty",    "empty",   "wire_off", "wire_on", "wire_on",
                             "wire_on", "wire_on", "wire_on", "wire_on"),
            ),
            "logic_layout": (
                ("input_on", "conn_on", "conn_on", "conn_on", "conn_on", "output_off"),
            ),
            "choices": [
                "15 (최대 강도)",
                "1 (약한 신호)",
                "0 (신호 없음)",
                "8 (절반)",
            ],
            "answer_index": 2,
            "explanation": (
                "레드스톤 신호는 15블록까지만 전달됩니다. "
                "16번째 블록에서 강도가 0이 되어 신호가 소멸합니다. "
                "리피터를 중간에 배치하면 강도를 15로 갱신하여 신호를 더 멀리 보낼 수 있습니다."
            ),
            "difficulty": "medium",
            "topic": "signal_strength",
        },
        # ── Q9 ── 리피터로 신호 연장 (S자 16블록 + 리피터) ──────────────────
        {
            "id": 9,
            "level": "basic",
            "title": "리피터로 신호 연장",
            "description": (
                "16블록 거리 중간(8번째)에 **리피터**를 배치했습니다. "
                "S자 회로 끝 램프의 상태는?\n\n"
                "> 리피터는 신호 강도를 15로 재충전합니다."
            ),
            "circuit_layout": (
                ("lever_on", "wire_on",  "wire_on", "wire_on", "wire_on",
                             "wire_on",  "wire_on", "repeater_on", "wire_on"),
                ("empty",    "empty",    "empty",   "empty",   "empty",
                             "empty",    "empty",   "empty",   "wire_on"),
                ("lamp_on",  "wire_on",  "wire_on", "wire_on", "wire_on",
                             "wire_on",  "wire_on", "wire_on", "wire_on"),
            ),
            "logic_layout": (
                ("input_on", "conn_on", "conn_on", "gate_buffer", "conn_on", "output_on"),
            ),
            "choices": [
                "켜짐 (ON)",
                "꺼짐 (OFF)",
                "신호 강도가 낮아 깜빡임",
                "리피터 오작동",
            ],
            "answer_index": 0,
            "explanation": (
                "리피터는 신호를 받으면 강도를 15로 갱신하여 출력합니다. "
                "8번째 리피터가 신호를 재충전하므로 16블록 끝 램프까지 신호가 전달됩니다. "
                "버퍼 게이트와 동일한 역할입니다."
            ),
            "difficulty": "hard",
            "topic": "repeater",
        },
        # ── Q10 ── OR 게이트 ──────────────────────────────────────────────
        {
            "id": 10,
            "level": "basic",
            "title": "OR 게이트",
            "description": (
                "두 개의 레버가 하나의 와이어로 합쳐지는 회로입니다. "
                "레버 A(위)만 켜고 레버 B(아래)는 끈 상태에서 램프의 상태는?\n\n"
                "> 레드스톤 와이어는 여러 신호 중 가장 강한 신호를 전달합니다.\n\n"
                "> 마인크래프트 회로에서는 신호가 **양방향**으로 전파됩니다."
            ),
            "circuit_layout": (
                ("lever_on",  "wire_on",  "empty",   "empty"  ),
                ("empty",     "wire_on",  "wire_on", "lamp_on"),
                ("lever_off", "wire_on",  "empty",   "empty"  ),
            ),
            "logic_layout": (
                ("input_on",  "conn_on",  "empty",    "empty"    ),
                ("empty",     "gate_or",  "conn_on",  "output_on"),
                ("input_off", "conn_off", "empty",    "empty"    ),
            ),
            "choices": [
                "켜짐 (ON)",
                "꺼짐 (OFF)",
                "두 신호가 충돌해 오류 발생",
                "깜빡임",
            ],
            "answer_index": 0,
            "explanation": (
                "레드스톤 와이어는 OR 게이트처럼 동작합니다. "
                "두 입력 중 하나라도 1이면 출력이 1입니다. "
                "논리식: 출력 = A OR B = 1 OR 0 = 1.\n\n"
                "※ 마인크래프트 회로에서는 신호가 와이어를 통해 양방향으로 전파되므로, "
                "레버 B 옆 와이어에도 레버 A의 신호가 흘러들어와 켜집니다. "
                "논리 회로와 달리 마인크래프트 와이어는 방향성이 없다는 점이 차이입니다."
            ),
            "difficulty": "hard",
            "topic": "logic_gate",
        },

        # ══════════════════════════════════════════════════════════════════════
        # 고급 레벨 (Q11–Q20)
        # ══════════════════════════════════════════════════════════════════════

        # ── Q11 ── AND 게이트 (A=1, B=1 → ON) ───────────────────────────────
        # 구현: NOT(A) OR NOT(B)의 반전 = NOR(NOT A, NOT B) = AND
        # A=1 → torch_off, B=1 → torch_off → NOR block 미활성 → NOR torch ON → lamp ON
        {
            "id": 11,
            "level": "advanced",
            "title": "AND 게이트",
            "description": (
                "레버 A(위)와 B(아래)가 모두 켜진 AND 게이트 회로입니다. "
                "램프의 상태는?\n\n"
                "> AND 게이트는 두 입력이 **모두 1**일 때만 출력이 1입니다.\n\n"
                "> 마인크래프트에서 AND는 두 NOT 게이트 출력을 NOR로 합쳐 구현합니다."
            ),
            "circuit_layout": (
                ("lever_on",  "wire_on",  "block",    "torch_off", "empty",    "empty",    "empty",    "empty"),
                ("empty",     "empty",    "empty",    "wire_off",  "wire_off", "block",    "torch_on", "lamp_on"),
                ("lever_on",  "wire_on",  "block",    "torch_off", "empty",    "empty",    "empty",    "empty"),
            ),
            "logic_layout": (
                ("input_on",  "conn_on",  "empty",    "empty",     "empty"),
                ("empty",     "gate_and", "conn_on",  "output_on", "empty"),
                ("input_on",  "conn_on",  "empty",    "empty",     "empty"),
            ),
            "choices": ["켜짐 (ON)", "꺼짐 (OFF)", "깜빡임", "알 수 없음"],
            "answer_index": 0,
            "explanation": (
                "AND 게이트: 두 입력이 모두 1일 때만 출력 1. "
                "A=1, B=1 → AND = 1 → 램프 켜짐.\n\n"
                "마인크래프트 구현: NOT(A)=0, NOT(B)=0 → 두 횃불 모두 꺼짐 → "
                "NOR 블록 비활성 → NOR 횃불 켜짐 → 램프 ON."
            ),
            "difficulty": "medium",
            "topic": "and_gate",
        },
        # ── Q12 ── AND 게이트 (A=1, B=0 → OFF) ──────────────────────────────
        {
            "id": 12,
            "level": "advanced",
            "title": "AND 게이트 — 한 입력 꺼짐",
            "description": (
                "AND 게이트 회로에서 레버 A(위)는 켜고 B(아래)는 끈 상태입니다. "
                "램프의 상태는?\n\n"
                "> AND 게이트는 두 입력이 **모두 1**일 때만 출력이 1입니다."
            ),
            "circuit_layout": (
                ("lever_on",  "wire_on",  "block",    "torch_off", "empty",    "empty",     "empty",    "empty"),
                ("empty",     "empty",    "empty",    "wire_on",   "wire_on",  "block",     "torch_off", "lamp_off"),
                ("lever_off", "wire_off", "block",    "torch_on",  "empty",    "empty",     "empty",    "empty"),
            ),
            "logic_layout": (
                ("input_on",  "conn_on",  "empty",     "empty",      "empty"),
                ("empty",     "gate_and", "conn_off",  "output_off", "empty"),
                ("input_off", "conn_off", "empty",     "empty",      "empty"),
            ),
            "choices": ["켜짐 (ON)", "꺼짐 (OFF)", "깜빡임", "알 수 없음"],
            "answer_index": 1,
            "explanation": (
                "AND 게이트: 입력 중 하나라도 0이면 출력 0. "
                "A=1, B=0 → AND = 0 → 램프 꺼짐.\n\n"
                "마인크래프트 구현: NOT(A)=0, NOT(B)=1 → B 쪽 횃불이 켜짐 → "
                "NOR 블록 활성화 → NOR 횃불 꺼짐 → 램프 OFF."
            ),
            "difficulty": "medium",
            "topic": "and_gate",
        },
        # ── Q13 ── NAND 게이트 (A=1, B=1 → OFF) ─────────────────────────────
        # 구현: NOT(A) OR NOT(B) → NAND
        # A=1 → torch_off, B=1 → torch_off → 합산 와이어 신호 없음 → lamp OFF
        {
            "id": 13,
            "level": "advanced",
            "title": "NAND 게이트",
            "description": (
                "레버 A(위)와 B(아래)가 모두 켜진 NAND 게이트 회로입니다. "
                "램프의 상태는?\n\n"
                "> NAND = NOT(A AND B). 두 입력이 모두 1일 때만 출력이 0입니다.\n\n"
                "> 드 모르간 법칙: NOT(A AND B) = NOT(A) OR NOT(B)"
            ),
            "circuit_layout": (
                ("lever_on",  "wire_on",  "block",    "torch_off", "wire_off", "empty",    "empty"),
                ("empty",     "empty",    "empty",    "empty",     "wire_off", "wire_off", "lamp_off"),
                ("lever_on",  "wire_on",  "block",    "torch_off", "wire_off", "empty",    "empty"),
            ),
            "logic_layout": (
                ("input_on",  "conn_on",  "empty",     "empty",      "empty"),
                ("empty",     "gate_nand","conn_off",  "output_off", "empty"),
                ("input_on",  "conn_on",  "empty",     "empty",      "empty"),
            ),
            "choices": ["켜짐 (ON)", "꺼짐 (OFF)", "깜빡임", "알 수 없음"],
            "answer_index": 1,
            "explanation": (
                "NAND(1, 1) = NOT(1 AND 1) = NOT(1) = 0 → 램프 꺼짐.\n\n"
                "드 모르간 법칙으로 구현: NOT(A) OR NOT(B) = 0 OR 0 = 0. "
                "두 NOT 게이트의 출력이 모두 0이므로 합산 와이어에 신호가 없어 램프가 꺼집니다."
            ),
            "difficulty": "hard",
            "topic": "nand_gate",
        },
        # ── Q14 ── NAND 게이트 (A=0, B=1 → ON) ──────────────────────────────
        {
            "id": 14,
            "level": "advanced",
            "title": "NAND 게이트 — 한 입력 꺼짐",
            "description": (
                "NAND 게이트에서 레버 A(위)는 끄고 B(아래)는 켠 상태입니다. "
                "램프의 상태는?\n\n"
                "> NAND = NOT(A AND B)"
            ),
            "circuit_layout": (
                ("lever_off", "wire_off", "block",    "torch_on",  "wire_on",  "empty",    "empty"),
                ("empty",     "empty",    "empty",    "empty",     "wire_on",  "wire_on",  "lamp_on"),
                ("lever_on",  "wire_on",  "block",    "torch_off", "wire_on",  "empty",    "empty"),
            ),
            "logic_layout": (
                ("input_off", "conn_off", "empty",    "empty",    "empty"),
                ("empty",     "gate_nand","conn_on",  "output_on","empty"),
                ("input_on",  "conn_on",  "empty",    "empty",    "empty"),
            ),
            "choices": ["켜짐 (ON)", "꺼짐 (OFF)", "깜빡임", "알 수 없음"],
            "answer_index": 0,
            "explanation": (
                "NAND(0, 1) = NOT(0 AND 1) = NOT(0) = 1 → 램프 켜짐.\n\n"
                "드 모르간 구현: NOT(A=0) = 1 → A 쪽 횃불이 켜짐 → "
                "합산 와이어에 신호 있음 → 램프 ON. "
                "NAND 게이트는 두 입력이 모두 1일 때만 꺼집니다."
            ),
            "difficulty": "hard",
            "topic": "nand_gate",
        },
        # ── Q15 ── NOR 게이트 (A=0, B=0 → ON) ───────────────────────────────
        {
            "id": 15,
            "level": "advanced",
            "title": "NOR 게이트",
            "description": (
                "레버 A(위)와 B(아래)가 모두 꺼진 NOR 게이트 회로입니다. "
                "램프의 상태는?\n\n"
                "> NOR = NOT(A OR B). 두 입력이 모두 0일 때만 출력이 1입니다."
            ),
            "circuit_layout": (
                ("lever_off", "wire_off", "empty",    "empty",     "empty",    "empty"),
                ("empty",     "wire_off", "wire_off", "block",     "torch_on", "lamp_on"),
                ("lever_off", "wire_off", "empty",    "empty",     "empty",    "empty"),
            ),
            "logic_layout": (
                ("input_off", "conn_off", "empty",    "empty",    "empty"),
                ("empty",     "gate_nor", "conn_on",  "output_on","empty"),
                ("input_off", "conn_off", "empty",    "empty",    "empty"),
            ),
            "choices": ["켜짐 (ON)", "꺼짐 (OFF)", "깜빡임", "알 수 없음"],
            "answer_index": 0,
            "explanation": (
                "NOR(0, 0) = NOT(0 OR 0) = NOT(0) = 1 → 램프 켜짐.\n\n"
                "두 레버가 모두 꺼지면 합산 와이어에 신호가 없어 블록이 비활성화되고 "
                "횃불이 켜져 램프에 신호가 전달됩니다."
            ),
            "difficulty": "medium",
            "topic": "nor_gate",
        },
        # ── Q16 ── NOR 게이트 (A=1, B=0 → OFF) ──────────────────────────────
        {
            "id": 16,
            "level": "advanced",
            "title": "NOR 게이트 — 한 입력 켜짐",
            "description": (
                "NOR 게이트에서 레버 A(위)는 켜고 B(아래)는 끈 상태입니다. "
                "램프의 상태는?\n\n"
                "> NOR = NOT(A OR B)"
            ),
            "circuit_layout": (
                ("lever_on",  "wire_on",  "empty",    "empty",     "empty",    "empty"),
                ("empty",     "wire_on",  "wire_on",  "block",     "torch_off","lamp_off"),
                ("lever_off", "wire_on",  "empty",    "empty",     "empty",    "empty"),
            ),
            "logic_layout": (
                ("input_on",  "conn_on",  "empty",     "empty",      "empty"),
                ("empty",     "gate_nor", "conn_off",  "output_off", "empty"),
                ("input_off", "conn_off", "empty",     "empty",      "empty"),
            ),
            "choices": ["켜짐 (ON)", "꺼짐 (OFF)", "깜빡임", "알 수 없음"],
            "answer_index": 1,
            "explanation": (
                "NOR(1, 0) = NOT(1 OR 0) = NOT(1) = 0 → 램프 꺼짐.\n\n"
                "A=1 신호가 와이어를 통해 블록에 전달되어 블록이 활성화되고 "
                "횃불이 꺼져 램프도 꺼집니다. NOR은 입력 중 하나라도 1이면 출력이 0입니다."
            ),
            "difficulty": "medium",
            "topic": "nor_gate",
        },
        # ── Q17 ── XOR 게이트 (A=1, B=0 → ON) ───────────────────────────────
        # 구현 원리 (5행 대칭 구조):
        #   행0/4: 레버 → 와이어 → 와이어 → 블럭A/B → 횟불_nA/nB → (열5)
        #   행1/3: (열1) 와이어 (열3) 와이어 (열5) 와이어
        #   행2 중앙: 블럭_cross(2,1) + 횟불_cross(2,2) + (열3) + (열5) + 와이어 + 조명
        #
        # 신호 경로: NOT_B 횟불(켜짐) → 열5 와이어 → 조명
        # 교차 횟불(꺼짐): 블럭A가 (1,1) 신호로 활성화 → 교차 횟불 OFF → 열3 신호 없음
        {
            "id": 17,
            "level": "advanced",
            "title": "XOR 게이트 — 입력이 다를 때",
            "description": (
                "레버 A(위쪽)는 켜고 B(아래쪽)는 끈 XOR 게이트 회로입니다. "
                "램프의 상태는?\n\n"
                "> XOR = '둘 중 하나만 1일 때' 출력 1. 둘 다 같으면 출력 0.\n\n"
                "> 논리식: A XOR B = (A AND NOT B) OR (NOT A AND B)"
            ),
            "circuit_layout": (
                ("lever_on",  "wire_on",  "wire_on",  "block",    "torch_off", "wire_on",  "empty",    "empty"),
                ("empty",     "wire_on",  "empty",    "wire_off", "empty",     "wire_on",  "empty",    "empty"),
                ("empty",     "block",    "torch_off","wire_off", "empty",     "wire_on",  "wire_on",  "lamp_on"),
                ("empty",     "wire_off", "empty",    "wire_off", "empty",     "wire_on",  "empty",    "empty"),
                ("lever_off", "wire_off", "wire_off", "block",    "torch_on",  "wire_on",  "empty",    "empty"),
            ),
            "logic_layout": (
                ("input_on",  "conn_on",  "empty",    "empty",    "empty"),
                ("empty",     "gate_xor", "conn_on",  "output_on","empty"),
                ("input_off", "conn_off", "empty",    "empty",    "empty"),
            ),
            "choices": ["켜짐 (ON)", "꺼짐 (OFF)", "깜빡임", "알 수 없음"],
            "answer_index": 0,
            "explanation": (
                "XOR(1, 0) = 1 → 램프 켜짐. 두 입력이 다를 때 XOR 출력은 1입니다.\n\n"
                "A=1 → 블록A 활성화 → NOT_A 횃불 꺼짐. A 신호(열1)가 중앙 블록도 활성화 → 교차 횃불 꺼짐.\n"
                "B=0 → 블록B 비활성 → NOT_B 횃불 켜짐 → 오른쪽 열5 와이어 전체에 신호 → 램프 ON.\n\n"
                "핵심: 중앙 교차 횃불이 꺼져 열3 와이어에 신호가 없으므로 블록A·B에 간섭 없음."
            ),
            "difficulty": "hard",
            "topic": "xor_gate",
        },
        # ── Q18 ── XOR 게이트 (A=1, B=1 → OFF) ──────────────────────────────
        # A=1, B=1: 블록A/B 모두 활성 → NOT_A/NOT_B 횃불 모두 꺼짐 → 열5 신호 없음 → 조명 OFF
        {
            "id": 18,
            "level": "advanced",
            "title": "XOR 게이트 — 두 입력이 같을 때",
            "description": (
                "레버 A(위쪽)와 B(아래쪽)가 모두 켜진 XOR 게이트 회로입니다. "
                "램프의 상태는?\n\n"
                "> XOR = '둘 중 하나만 1일 때' 출력 1. 둘 다 같으면 출력 0."
            ),
            "circuit_layout": (
                ("lever_on",  "wire_on",  "wire_on",  "block",    "torch_off", "wire_off", "empty",    "empty"),
                ("empty",     "wire_on",  "empty",    "wire_off", "empty",     "wire_off", "empty",    "empty"),
                ("empty",     "block",    "torch_off","wire_off", "empty",     "wire_off", "wire_off", "lamp_off"),
                ("empty",     "wire_on",  "empty",    "wire_off", "empty",     "wire_off", "empty",    "empty"),
                ("lever_on",  "wire_on",  "wire_on",  "block",    "torch_off", "wire_off", "empty",    "empty"),
            ),
            "logic_layout": (
                ("input_on",  "conn_on",  "empty",     "empty",      "empty"),
                ("empty",     "gate_xor", "conn_off",  "output_off", "empty"),
                ("input_on",  "conn_on",  "empty",     "empty",      "empty"),
            ),
            "choices": ["켜짐 (ON)", "꺼짐 (OFF)", "깜빡임", "알 수 없음"],
            "answer_index": 1,
            "explanation": (
                "XOR(1, 1) = 0 → 램프 꺼짐. 두 입력이 같을 때 XOR 출력은 0입니다.\n\n"
                "A=1, B=1 → 블록A·B 모두 활성화 → NOT_A·NOT_B 횃불 모두 꺼짐 → 열5 와이어 신호 없음 → 램프 OFF.\n\n"
                "교차 횃불도 꺼져 있어 열3에 신호 없음. XOR(0,0)도 같은 원리로 0입니다."
            ),
            "difficulty": "hard",
            "topic": "xor_gate",
        },
        # ── Q19 ── 3입력 OR (A=0, B=1, C=0 → ON) ────────────────────────────
        {
            "id": 19,
            "level": "advanced",
            "title": "3입력 OR 게이트",
            "description": (
                "세 개의 레버 A(위), B(중간), C(아래)가 하나의 와이어로 합쳐지는 회로입니다. "
                "레버 B만 켜진 상태에서 램프의 상태는?\n\n"
                "> OR 게이트는 입력 중 **하나라도** 1이면 출력이 1입니다."
            ),
            "circuit_layout": (
                ("lever_off", "wire_on",  "empty",    "empty",    "empty"),
                ("lever_on",  "wire_on",  "wire_on",  "wire_on",  "lamp_on"),
                ("lever_off", "wire_on",  "empty",    "empty",    "empty"),
            ),
            "logic_layout": (
                ("input_off", "conn_off", "empty",    "empty",    "empty"),
                ("input_on",  "gate_or",  "conn_on",  "output_on","empty"),
                ("input_off", "conn_off", "empty",    "empty",    "empty"),
            ),
            "choices": ["켜짐 (ON)", "꺼짐 (OFF)", "깜빡임", "알 수 없음"],
            "answer_index": 0,
            "explanation": (
                "OR(0, 1, 0) = 1 → 램프 켜짐.\n\n"
                "레버 B의 신호가 와이어를 통해 합산 지점으로 전달되어 램프를 켭니다. "
                "레드스톤 와이어는 연결된 레버 중 가장 강한 신호를 선택하므로, "
                "B=1 하나만으로도 출력이 1이 됩니다."
            ),
            "difficulty": "medium",
            "topic": "or_gate",
        },
        # ── Q20 ── 드 모르간: NOT(A OR B) (A=0, B=0 → ON) ───────────────────
        {
            "id": 20,
            "level": "advanced",
            "title": "드 모르간 법칙 — NOT(A OR B)",
            "description": (
                "레버 A(위)와 B(아래)가 모두 꺼진 회로입니다. "
                "NOT(A OR B) 회로에서 램프의 상태는?\n\n"
                "> 드 모르간 법칙: **NOT(A OR B) = NOT(A) AND NOT(B)**\n\n"
                "> 두 NOT 게이트 출력을 AND 결합한 결과와 동일합니다."
            ),
            "circuit_layout": (
                ("lever_off", "wire_off", "block",    "torch_on",  "wire_on",  "empty",    "empty"),
                ("empty",     "empty",    "empty",    "empty",     "wire_on",  "wire_on",  "lamp_on"),
                ("lever_off", "wire_off", "block",    "torch_on",  "wire_on",  "empty",    "empty"),
            ),
            "logic_layout": (
                ("input_off", "conn_off", "empty",    "empty",    "empty"),
                ("empty",     "gate_nor", "conn_on",  "output_on","empty"),
                ("input_off", "conn_off", "empty",    "empty",    "empty"),
            ),
            "choices": ["켜짐 (ON)", "꺼짐 (OFF)", "깜빡임", "알 수 없음"],
            "answer_index": 0,
            "explanation": (
                "NOT(A OR B) = NOT(0 OR 0) = NOT(0) = 1 → 램프 켜짐.\n\n"
                "드 모르간 법칙에 의해 NOT(A OR B) = NOT(A) AND NOT(B) = 1 AND 1 = 1.\n\n"
                "마인크래프트 회로: A=0 → NOT(A)=1 (횃불 켜짐), B=0 → NOT(B)=1 (횃불 켜짐). "
                "두 횃불의 신호가 합산되어 램프에 전달됩니다. "
                "이것은 NOR 게이트와 동일한 동작입니다."
            ),
            "difficulty": "hard",
            "topic": "de_morgan",
        },
    ]
    return [q for q in all_questions if q.get("level", "basic") == level]
