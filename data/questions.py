import streamlit as st


@st.cache_data
def load_questions() -> list:
    """
    퀴즈 문항 로드.

    캐싱 이유: 문항 데이터는 앱 실행 중 변하지 않습니다.
    Streamlit은 위젯 조작 시마다 스크립트를 재실행하므로,
    @st.cache_data 없이는 라디오 버튼 클릭마다 리스트를 재생성합니다.
    캐싱으로 최초 1회만 생성하고 이후에는 캐시에서 즉시 반환합니다.

    circuit_layout: 마인크래프트 회로 스프라이트 2D 튜플
    logic_layout:   논리 게이트 다이어그램 스프라이트 2D 튜플
    두 layout 모두 circuit_renderer.render_circuit_image()로 렌더링됩니다.
    """
    return [
        # ── Q1 ── 기본 회로 (켜짐) ─────────────────────────────────────────
        {
            "id": 1,
            "title": "기본 레드스톤 회로",
            "description": (
                "레버가 **켜져** 있습니다. "
                "레드스톤 와이어로 연결된 램프의 상태는?"
            ),
            "circuit_layout": (
                ("lever_on", "wire_on", "wire_on", "wire_on", "lamp_on"),
            ),
            "logic_layout": (
                ("input_on", "wire_on", "wire_on", "wire_on", "output_on"),
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
            "title": "꺼진 레버",
            "description": (
                "레버가 **꺼져** 있습니다. "
                "램프의 상태는?"
            ),
            "circuit_layout": (
                ("lever_off", "wire_off", "wire_off", "wire_off", "lamp_off"),
            ),
            "logic_layout": (
                ("input_off", "wire_off", "wire_off", "wire_off", "output_off"),
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
            "title": "리피터 통과",
            "description": (
                "레버가 켜져 있고, 회로 중간에 **리피터**가 있습니다. "
                "램프의 상태는?"
            ),
            "circuit_layout": (
                ("lever_on", "wire_on", "repeater_on", "wire_on", "lamp_on"),
            ),
            "logic_layout": (
                ("input_on", "wire_on", "gate_buffer", "wire_on", "output_on"),
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
            "title": "NOT 게이트 — 꺼진 입력",
            "description": (
                "레버가 **꺼져** 있습니다. "
                "블록 측면에 횃불이 부착된 NOT 게이트 회로입니다. "
                "램프의 상태는?\n\n"
                "> 횃불은 블록이 비활성화 상태일 때 켜집니다."
            ),
            "circuit_layout": (
                ("lever_off", "wire_off", "block",    "lamp_on"),
                ("empty",     "empty",    "torch_on", "empty"  ),
            ),
            "logic_layout": (
                ("input_off", "wire_off", "gate_not", "output_on"),
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
            "title": "NOT 게이트 — 켜진 입력",
            "description": (
                "레버가 **켜져** 있습니다. "
                "동일한 NOT 게이트 회로에서 램프의 상태는?\n\n"
                "> 횃불은 블록이 활성화되면 꺼집니다."
            ),
            "circuit_layout": (
                ("lever_on", "wire_on", "block",     "lamp_off"),
                ("empty",    "empty",   "torch_off", "empty"   ),
            ),
            "logic_layout": (
                ("input_on", "wire_on", "gate_not", "output_off"),
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
            "title": "리피터의 방향성",
            "description": (
                "리피터는 **오른쪽(→)** 방향입니다. "
                "레버는 오른쪽에 있고 램프는 왼쪽에 있습니다. "
                "램프의 상태는?\n\n"
                "> 리피터는 신호를 한 방향으로만 통과시킵니다."
            ),
            "circuit_layout": (
                ("lamp_off", "wire_off", "repeater_off", "wire_on", "lever_on"),
            ),
            "logic_layout": (
                ("output_off", "wire_off", "gate_buffer", "wire_on", "input_on"),
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
            "title": "이중 NOT 게이트 (버퍼)",
            "description": (
                "레버가 **켜져** 있습니다. "
                "NOT 게이트 두 개가 직렬로 연결된 회로입니다. "
                "최종 램프의 상태는?"
            ),
            "circuit_layout": (
                ("lever_on", "wire_on", "block",     "wire_off", "block",    "lamp_on"),
                ("empty",    "empty",   "torch_off", "empty",    "torch_on", "empty"  ),
            ),
            "logic_layout": (
                ("input_on", "wire_on", "gate_not", "wire_off", "gate_not", "output_on"),
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
        # ── Q8 ── 신호 강도 한계 ──────────────────────────────────────────
        {
            "id": 8,
            "title": "신호 강도 한계",
            "description": (
                "레드스톤 신호는 최대 강도 **15**이며, 1블록 이동마다 1씩 감소합니다. "
                "레버에서 **16블록** 떨어진 위치의 신호 강도는?"
            ),
            "circuit_layout": (
                ("lever_on", "wire_on", "wire_on", "wire_on", "wire_on", "wire_off"),
            ),
            "logic_layout": (
                ("input_on", "wire_on", "wire_on", "wire_on", "wire_on", "output_off"),
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
        # ── Q9 ── 리피터로 신호 연장 ──────────────────────────────────────
        {
            "id": 9,
            "title": "리피터로 신호 연장",
            "description": (
                "16블록 거리 중간에 **리피터**를 배치했습니다. "
                "리피터 이후 램프의 상태는?"
            ),
            "circuit_layout": (
                ("lever_on", "wire_on", "wire_on", "repeater_on", "wire_on", "lamp_on"),
            ),
            "logic_layout": (
                ("input_on", "wire_on", "wire_on", "gate_buffer", "wire_on", "output_on"),
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
                "이를 통해 15블록 이상의 거리도 신호를 전달할 수 있습니다. "
                "버퍼 게이트와 동일한 역할입니다."
            ),
            "difficulty": "hard",
            "topic": "repeater",
        },
        # ── Q10 ── OR 게이트 ──────────────────────────────────────────────
        {
            "id": 10,
            "title": "OR 게이트",
            "description": (
                "레버 A(위)는 **켜져** 있고, 레버 B(아래)는 **꺼져** 있습니다. "
                "두 신호가 하나의 와이어로 합쳐질 때 램프의 상태는?\n\n"
                "> 레드스톤 와이어는 여러 신호 중 가장 강한 신호를 전달합니다."
            ),
            "circuit_layout": (
                ("lever_on",  "wire_on",  "wire_on",  "lamp_on" ),
                ("lever_off", "wire_off", "empty",    "empty"   ),
            ),
            "logic_layout": (
                ("input_on",  "wire_on",  "gate_or",  "output_on"),
                ("input_off", "wire_off", "empty",    "empty"   ),
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
                "논리식: 출력 = A OR B = 1 OR 0 = 1."
            ),
            "difficulty": "hard",
            "topic": "logic_gate",
        },
    ]
