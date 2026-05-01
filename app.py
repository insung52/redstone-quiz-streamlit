import time

import streamlit as st

from auth import verify_login
from circuit_renderer import (
    compute_signal_strengths,
    get_animation_frames,
    mask_answers,
    render_circuit_frame,
    render_circuit_image,
)
from data.questions import load_questions
from quiz_engine import calculate_score, get_grade

# ── 제출자 정보 (과제 필수: 첫 화면에 표시) ────────────────────────────────
STUDENT_ID = "2021204042"
STUDENT_NAME = "황인성"

DIFFICULTY_LABEL = {"easy": "🟢 쉬움", "medium": "🟡 중간", "hard": "🔴 어려움"}


# ── 세션 상태 초기화 ────────────────────────────────────────────────────────
def init_session_state() -> None:
    defaults = {
        "page": "home",
        "logged_in": False,
        "username": "",
        "login_attempts": 0,
        "level": None,          # "basic" | "advanced"
        "current_q": 0,
        "answers": {},
        "show_logic": False,    # 논리 회로 보기 토글
        "quiz_state": "answering",  # "answering" | "animating" | "answered"
        "current_answer": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def reset_quiz() -> None:
    """퀴즈 진행 상태만 초기화 (로그인 유지, 레벨 선택으로 복귀)."""
    st.session_state.current_q = 0
    st.session_state.answers = {}
    st.session_state.show_logic = False
    st.session_state.quiz_state = "answering"
    st.session_state.current_answer = None
    st.session_state.level = None
    st.session_state.page = "home"


# ── 페이지: 홈 ──────────────────────────────────────────────────────────────
def page_home() -> None:
    st.title("레드스톤으로 배우는 논리회로")

    # 과제 필수: 학번/이름 첫 화면 표시
    st.info(f"학번: {STUDENT_ID}  |  이름: {STUDENT_NAME}")
    st.image("redstone.png", use_container_width=True)

    st.markdown(
        """
마인크래프트 **레드스톤 회로**는 현실의 논리 회로와 동일한 원리로 동작합니다.

퀴즈를 풀며 **AND / OR / NOT / 버퍼** 같은 논리 게이트 개념을 자연스럽게 익혀보세요!

- 각 문제마다 **마인크래프트 회로 ↔ 논리 게이트 다이어그램** 전환 가능
- 마인크래프트를 몰라도 논리 회로 보기로 충분히 풀 수 있습니다
- 풀이 후 오답 해설과 주제별 성취도를 확인할 수 있습니다
        """
    )

    st.markdown("---")
    st.subheader("난이도 선택")

    col_basic, col_adv = st.columns(2)
    with col_basic:
        st.markdown("### 🟢 기초 레벨")
        st.markdown(
            "- 10문제 (쉬움 ~ 어려움)\n"
            "- 레드스톤 기본 동작\n"
            "- NOT 게이트, 리피터\n"
            "- 신호 강도 & OR 게이트"
        )
        if st.button("기초 레벨 시작", type="primary", use_container_width=True):
            print("[LOG] 기초 레벨 시작 버튼 클릭")
            st.session_state.level = "basic"
            st.session_state.page = "quiz" if st.session_state.logged_in else "login"
            st.rerun()

    with col_adv:
        st.markdown("### 🔴 고급 레벨")
        st.markdown(
            "- 10문제 (중간 ~ 어려움)\n"
            "- AND / NAND / NOR 게이트\n"
            "- XOR 게이트\n"
            "- 드 모르간 법칙 응용"
        )
        if st.button("고급 레벨 시작", type="secondary", use_container_width=True):
            print("[LOG] 고급 레벨 시작 버튼 클릭")
            st.session_state.level = "advanced"
            st.session_state.page = "quiz" if st.session_state.logged_in else "login"
            st.rerun()


# ── 페이지: 로그인 ──────────────────────────────────────────────────────────
def page_login() -> None:
    st.title("로그인")
    st.info(f"학번: {STUDENT_ID}  |  이름: {STUDENT_NAME}")
    st.markdown("퀴즈를 풀려면 로그인이 필요합니다.")

    with st.form("login_form"):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인", use_container_width=True)

    if submitted:
        print(f"[LOG] 로그인 시도: {username.strip()}")
        if verify_login(username, password):
            print(f"[LOG] 로그인 성공: {username.strip()}")
            st.session_state.logged_in = True
            st.session_state.username = username.strip()
            st.session_state.login_attempts = 0
            # 레벨이 이미 선택되어 있으면 바로 quiz, 아니면 홈(레벨 선택)으로
            st.session_state.page = "quiz" if st.session_state.level else "home"
            st.rerun()
        else:
            print(f"[LOG] 로그인 실패: {username.strip()}")
            st.session_state.login_attempts += 1
            attempts = st.session_state.login_attempts
            st.error(
                f"아이디 또는 비밀번호가 올바르지 않습니다. (시도 횟수: {attempts}회)"
            )
            if attempts >= 5:
                st.warning("로그인 시도가 5회를 초과했습니다. 계정 정보를 확인하세요.")

    st.markdown("---")
    st.caption("테스트 계정: admin / admin123  |  user1 / pass1234")

    if st.button("← 홈으로"):
        st.session_state.page = "home"
        st.rerun()


# ── 페이지: 퀴즈 ──────────────────────────────────────────────────────────
def page_quiz() -> None:
    questions = load_questions(st.session_state.get("level", "basic"))
    q_idx = st.session_state.current_q
    total = len(questions)

    if q_idx >= total:
        st.session_state.page = "result"
        st.rerun()
        return

    q = questions[q_idx]
    quiz_state = st.session_state.quiz_state

    # ── 헤더 ──
    st.info(f"학번: {STUDENT_ID}  |  이름: {STUDENT_NAME}")
    col_title, col_user = st.columns([3, 1])
    with col_title:
        st.subheader(f"Q{q_idx + 1} / {total}  —  {q['title']}")
    with col_user:
        st.markdown(f"**{st.session_state.username}** 님")

    st.progress(q_idx / total, text=f"진행률: {q_idx}/{total}")
    st.markdown(f"{DIFFICULTY_LABEL.get(q['difficulty'], '')}  |  주제: `{q['topic']}`")
    st.markdown("---")
    st.markdown(q["description"])

    # ── 회로 보기 토글 (애니메이션 중에는 숨김) ──
    has_logic = bool(q.get("logic_layout"))
    if has_logic and quiz_state != "animating":
        view_col1, view_col2 = st.columns([1, 1])
        with view_col1:
            if st.button(
                "✅ 마인크래프트 회로 보기" if not st.session_state.show_logic else "🔴 마인크래프트 회로 보기",
                use_container_width=True,
            ):
                st.session_state.show_logic = False
                st.rerun()
        with view_col2:
            if st.button(
                "✅ 논리 회로 보기" if st.session_state.show_logic else "🔵 논리 회로 보기",
                use_container_width=True,
            ):
                st.session_state.show_logic = True
                st.rerun()

    layout = q["logic_layout"] if (st.session_state.show_logic and has_logic) else q["circuit_layout"]
    caption = "논리 게이트 다이어그램" if (st.session_state.show_logic and has_logic) else "마인크래프트 레드스톤 회로"

    # ── 상태별 분기 ──────────────────────────────────────────────────────
    if quiz_state == "answering":
        st.image(render_circuit_image(mask_answers(layout)), caption=caption)
        st.markdown("---")

        chosen_label = st.radio(
            "답을 선택하세요:",
            q["choices"],
            key=f"radio_q{q_idx}",
            index=None,
        )
        st.markdown("")

        if st.button(
            "답 확인하기 →",
            type="primary",
            use_container_width=True,
            disabled=(chosen_label is None),
        ):
            chosen_index = q["choices"].index(chosen_label)
            print(f"[LOG] Q{q_idx + 1} 답 제출: {chosen_label}")
            st.session_state.current_answer = chosen_index
            st.session_state.answers[q_idx] = chosen_index
            st.session_state.quiz_state = "animating"
            st.rerun()

        if chosen_label is None:
            st.caption("답을 선택해야 확인할 수 있습니다.")

    elif quiz_state == "animating":
        st.markdown("**🔴 레드스톤 신호가 전파되고 있습니다...**")
        placeholder = st.empty()
        for frame_layout, signal_strengths in get_animation_frames(layout):
            placeholder.image(
                render_circuit_frame(frame_layout, signal_strengths),
                caption=f"신호 전파 중 — {caption}",
            )
            time.sleep(0.35)
        st.session_state.quiz_state = "answered"
        st.rerun()

    elif quiz_state == "answered":
        st.image(render_circuit_frame(layout, compute_signal_strengths(layout)), caption=caption)
        st.markdown("---")

        chosen_index = st.session_state.current_answer
        correct = chosen_index == q["answer_index"]
        my_ans = q["choices"][chosen_index] if 0 <= chosen_index < len(q["choices"]) else "?"
        correct_ans = q["choices"][q["answer_index"]]

        if correct:
            st.success(f"✅ 정답입니다!  |  **{my_ans}**")
        else:
            st.error(f"❌ 오답입니다.  내 답: **{my_ans}**  →  정답: **{correct_ans}**")
        st.info(f"**해설:** {q['explanation']}")
        st.markdown("")

        next_label = "결과 보기 →" if q_idx + 1 >= total else "다음 문제 →"
        if st.button(next_label, type="primary", use_container_width=True):
            print(f"[LOG] Q{q_idx + 1} → {'결과 페이지' if q_idx + 1 >= total else f'Q{q_idx + 2}'}")
            st.session_state.quiz_state = "answering"
            st.session_state.current_answer = None
            st.session_state.show_logic = False
            if q_idx + 1 >= total:
                st.session_state.page = "result"
            else:
                st.session_state.current_q += 1
            st.rerun()


# ── 페이지: 결과 ──────────────────────────────────────────────────────────
def page_result() -> None:
    questions = load_questions(st.session_state.get("level", "basic"))
    answers = st.session_state.answers
    total = len(questions)
    level = st.session_state.get("level", "basic")
    score = calculate_score(answers, level)
    grade, grade_desc = get_grade(score, total)
    level_label = "🟢 기초 레벨" if level == "basic" else "🔴 고급 레벨"
    st.info(f"학번: {STUDENT_ID}  |  이름: {STUDENT_NAME}")
    st.title(f"퀴즈 결과  —  {level_label}")

    # ── 점수 / 등급 ──
    col1, col2 = st.columns(2)
    with col1:
        st.metric("최종 점수", f"{score} / {total}")
    with col2:
        st.metric("등급", grade)

    st.success(grade_desc)

    # ── 주제별 성취도 ──
    st.markdown("---")
    st.subheader("주제별 결과")
    topic_stats: dict = {}
    for i, q in enumerate(questions):
        t = q["topic"]
        correct = answers.get(i) == q["answer_index"]
        if t not in topic_stats:
            topic_stats[t] = {"correct": 0, "total": 0}
        topic_stats[t]["total"] += 1
        if correct:
            topic_stats[t]["correct"] += 1

    for topic, stat in topic_stats.items():
        ratio = stat["correct"] / stat["total"]
        bar_val = ratio
        st.write(f"**{topic}**: {stat['correct']}/{stat['total']}")
        st.progress(bar_val)

    # ── 문제별 정오 + 해설 ──
    st.markdown("---")
    st.subheader("문제별 풀이")
    for i, q in enumerate(questions):
        correct = answers.get(i) == q["answer_index"]
        icon = "✅" if correct else "❌"
        with st.expander(f"{icon}  Q{i + 1}. {q['title']}"):
            my_ans_idx = answers.get(i, -1)
            my_ans = (
                q["choices"][my_ans_idx]
                if 0 <= my_ans_idx < len(q["choices"])
                else "미응답"
            )
            correct_ans = q["choices"][q["answer_index"]]

            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**내 답:** {my_ans}")
            with col_b:
                st.write(f"**정답:** {correct_ans}")

            # 회로 이미지 (정답 상태)
            st.image(
                render_circuit_image(q["circuit_layout"]),
                caption="마인크래프트 회로",
                width=300,
            )
            if q.get("logic_layout"):
                st.image(
                    render_circuit_image(q["logic_layout"]),
                    caption="논리 회로",
                    width=300,
                )
            st.info(f"**해설:** {q['explanation']}")

    st.markdown("---")
    if st.button("다시 도전하기", type="primary", use_container_width=True):
        print("[LOG] 퀴즈 재시작")
        reset_quiz()
        st.rerun()

    if st.button("로그아웃"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ── 메인 라우터 ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="레드스톤으로 배우는 논리회로",
    page_icon="🔴",
    layout="centered",
)

init_session_state()

_page = st.session_state.page

if _page == "home":
    page_home()
elif _page == "login":
    page_login()
elif _page == "quiz":
    if not st.session_state.logged_in:
        st.session_state.page = "login"
        st.rerun()
    else:
        page_quiz()
elif _page == "result":
    if not st.session_state.logged_in:
        st.session_state.page = "login"
        st.rerun()
    else:
        page_result()
