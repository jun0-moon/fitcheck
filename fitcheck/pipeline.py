"""전체 Workflow: extract → match(병렬) → evaluate → verify → (재생성) → 결과."""
from dataclasses import dataclass, field

from .evaluate import evaluate_fit
from .extract import extract_requirements
from .llm import log_event
from .match import match_all
from .schemas import FitReport, JobRequirements, MatchResult
from .verify import find_ungrounded_sources


@dataclass
class RunResult:
    requirements: JobRequirements
    matches: list[MatchResult]
    report: FitReport
    verified: bool
    dropped_sources: list[str] = field(default_factory=list)


def run_pipeline(
    jd_text: str,
    projects: dict[str, str],
    max_regen: int = 1,  # 근거 검증 실패 시 평가 재생성 최대 횟수
) -> RunResult:
    requirements = extract_requirements(jd_text)
    matches = match_all(requirements, projects)

    feedback = ""
    bad: list[str] = []
    report = None
    for attempt in range(max_regen + 1):
        report = evaluate_fit(requirements, matches, feedback)
        bad = find_ungrounded_sources(report, projects)
        log_event(
            "verify",
            attempt=attempt,
            status="pass" if not bad else "fail",
            bad=bad,
        )
        if not bad:
            return RunResult(requirements, matches, report, verified=True)
        feedback = (
            "다음 sources 는 포트폴리오 원문에서 찾을 수 없다. "
            "match_data 의 evidence 문장만 그대로 사용하라: " + " | ".join(bad)
        )

    # 재생성 후에도 실패: 근거 없는 sources 는 빼고, 검증 실패로 표시한다
    report.sources = [s for s in report.sources if s not in bad]
    return RunResult(requirements, matches, report, verified=False, dropped_sources=bad)