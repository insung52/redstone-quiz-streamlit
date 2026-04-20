# 레드스톤으로 배우는 논리회로

마인크래프트 레드스톤 회로 이미지를 통해 AND, OR, NOT 등 논리 게이트 개념을 쉽게 학습하는 Streamlit 퀴즈 앱입니다.

**학번:** 2021204042 | **이름:** 황인성

---

## 실행 방법

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

테스트 계정: `admin` / `admin123`

---

## 주요 기능

- **기초 / 고급 레벨** — 난이도별 10문제씩, 총 20문제
- **레드스톤 신호 애니메이션** — 답 확인 시 BFS 방식으로 신호 전파를 시각화
- **논리 회로 뷰 전환** — 마인크래프트 회로 ↔ 논리 게이트 다이어그램 전환
- **결과 페이지** — 점수, 등급, 주제별 성취도, 문제별 해설 제공

## 프로젝트 구조

```
app.py                  # 메인 실행 파일 (페이지 라우팅)
auth.py                 # 로그인 인증
quiz_engine.py          # 점수 계산 및 등급 판정
circuit_renderer.py     # 레드스톤/논리 회로 이미지 렌더링
data/questions.py       # 퀴즈 문항 데이터
assets/sprites/         # 타일 스프라이트 이미지
```
