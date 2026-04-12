from data.questions import load_questions


def calculate_score(answers: dict, level: str = "basic") -> int:
    """
    answers: {question_index: chosen_index}
    정답과 비교하여 맞힌 문제 수 반환.
    """
    questions = load_questions(level)
    return sum(
        1
        for i, q in enumerate(questions)
        if answers.get(i) == q["answer_index"]
    )


def get_grade(score: int, total: int) -> tuple:
    """점수에 따른 (등급명, 설명) 반환."""
    ratio = score / total if total > 0 else 0
    if ratio == 1.0:
        return "레드스톤 마스터", "완벽합니다! 당신은 레드스톤의 신입니다. 어떤 회로도 설계할 수 있어요."
    elif ratio >= 0.8:
        return "레드스톤 엔지니어", "훌륭합니다! 대부분의 회로 원리를 정확히 이해하고 있습니다."
    elif ratio >= 0.6:
        return "레드스톤 견습생", "절반 이상 맞혔습니다! 조금 더 연습하면 엔지니어가 될 수 있어요."
    else:
        return "레드스톤 초보자", "레드스톤의 세계에 온 걸 환영합니다. 기초부터 차근차근 익혀봐요!"
