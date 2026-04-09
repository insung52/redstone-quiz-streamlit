import hashlib
import streamlit as st


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@st.cache_data
def load_user_db() -> dict:
    """
    사용자 DB 로드.

    캐싱 이유: 사용자 정보는 앱 실행 중 변경되지 않는 정적 데이터입니다.
    Streamlit은 위젯 조작 시마다 전체 스크립트를 재실행하므로,
    @st.cache_data 없이는 로그인 버튼 클릭 시마다 dict를 재구성합니다.
    캐싱을 통해 최초 1회만 생성하고 이후에는 캐시에서 즉시 반환합니다.

    테스트 계정:
      - 아이디: admin  / 비밀번호: admin123
      - 아이디: user1  / 비밀번호: pass1234
    """
    return {
        "admin": _hash("admin123"),
        "user1": _hash("pass1234"),
    }


def verify_login(username: str, password: str) -> bool:
    """아이디/비밀번호 검증. 비밀번호는 SHA-256 해시로 비교."""
    if not username or not password:
        return False
    db = load_user_db()
    return db.get(username.strip()) == _hash(password)
