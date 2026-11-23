"""3단계: 매칭 결과를 바탕으로 적합도·부족한 점·보완 제안을 만든다."""
import json

from .llm import generate_structured
from .schemas import FitReport, JobRequirements, MatchResult

SYSTEM = """너는 채용공고와 내 포트폴리오의 적합도를 평가하는 평가자다.
규칙:
- <match_data> 에 있는 사실만 근거로 쓴다. 거기에 없는 경험을 있다고 쓰지 않는다.
- strengths 는 근거가 있는 항목만, gaps 는 근거가 없거나(none) 부분적(partial)인 항목을 쓴다.
- suggestions 는 gaps 를 메우기 위한 구체적이고 현실적인 보완 방법을 쓴다.
- sources 에는 strengths 의 근거가 된 문장을 match_data 의 evidence 에서 그대로 복사해 넣는다.
- fit_level: 필수(required) 기술 대부분이 strong 이면 high, 일부만 strong/partial 이면 medium,
  대부분 none/partial 이면 low.
"""


def evaluate_fit(
    requirements: JobRequirements,
    matches: list[MatchResult],
    feedback: str = "",
) -> FitReport:
    payload = json.dumps(
        {
            "job": requirements.model_dump(),
            "matches": [m.model_dump() for m in matches],
        },
        ensure_ascii=False,
    )
    prompt = f"<match_data>\n{payload}\n</match_data>\n\n적합도 리포트를 작성하라."
    if feedback:
        prompt += f"\n\n[이전 시도에서 지적된 문제]\n{feedback}"
    return generate_structured(
        step="evaluate",
        prompt=prompt,
        schema=FitReport,
        system=SYSTEM,
    )