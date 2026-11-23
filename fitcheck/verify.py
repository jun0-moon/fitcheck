"""4단계: 리포트의 근거가 실제 포트폴리오에 있는지 코드로 검증한다.

주의: 확인하는 것은 'sources 의 문장이 포트폴리오 원문에 존재하는가' 이다.
strengths 문장이 근거와 의미상 맞는지까지는 확인하지 못한다(README 한계 참고).
"""
from .extract import is_grounded
from .portfolio import portfolio_as_text
from .schemas import FitReport


def find_ungrounded_sources(report: FitReport, projects: dict[str, str]) -> list[str]:
    full_text = portfolio_as_text(projects)
    bad = [s for s in report.sources if not is_grounded(s, full_text)]
    if report.strengths and not report.sources:
        bad.append("(strengths 가 있는데 sources 가 비어 있음)")
    return bad