"""5단계: 결과를 사람이 읽는 마크다운 리포트로 만든다."""
from .pipeline import RunResult

_LEVEL = {"high": "높음", "medium": "보통", "low": "낮음"}
_STRENGTH = {"strong": "강함", "partial": "부분", "none": "없음"}
_KIND = {"required": "필수", "preferred": "우대"}


def _cell(text: str) -> str:
    return text.replace("|", "/").replace("\n", " ")


def render_markdown(result: RunResult) -> str:
    req, rep = result.requirements, result.report
    kind_of = {s.name: s.kind for s in req.skills}

    lines = [
        f"# FitCheck 리포트: {req.company} / {req.position}",
        "",
        f"**적합도: {_LEVEL.get(rep.fit_level, rep.fit_level)}**",
        "",
        "## 요구 기술 매칭",
        "",
        "| 기술 | 구분 | 매칭 | 근거 프로젝트 |",
        "|---|---|---|---|",
    ]
    for m in result.matches:
        projects = ", ".join(sorted({e.project for e in m.evidences})) or "-"
        lines.append(
            f"| {_cell(m.skill)} | {_KIND.get(kind_of.get(m.skill, ''), '-')} "
            f"| {_STRENGTH.get(m.strength, m.strength)} | {_cell(projects)} |"
        )

    for title, items in (
        ("강점", rep.strengths),
        ("부족한 점", rep.gaps),
        ("보완 제안", rep.suggestions),
    ):
        lines += ["", f"## {title}", ""]
        lines += [f"- {i}" for i in items] or ["- (없음)"]

    lines += ["", "## 근거 (포트폴리오 원문)", ""]
    lines += [f"- {s}" for s in rep.sources] or ["- (없음)"]

    lines += ["", "## 검증 결과", ""]
    if result.verified:
        lines.append("- 통과: 모든 근거가 포트폴리오 원문에서 확인되었습니다.")
    else:
        lines.append("- 실패: 재생성 후에도 원문에서 확인되지 않은 근거가 있어 제외했습니다.")
        lines += [f"  - 제외됨: {s}" for s in result.dropped_sources]
    return "\n".join(lines) + "\n"