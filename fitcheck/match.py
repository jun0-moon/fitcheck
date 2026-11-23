"""2단계: 요구 기술별로 내 포트폴리오에서 근거를 찾는다 (Parallelization).

요구 기술끼리는 서로 독립적이라 병렬로 처리할 수 있다.
LLM이 댄 근거는 코드로 다시 검증한다(근거 문장이 해당 프로젝트 문서에 실제로 있는가).
"""
from concurrent.futures import ThreadPoolExecutor

from .extract import is_grounded
from .llm import generate_structured, log_event, wrap_untrusted
from .portfolio import portfolio_as_text
from .schemas import JobRequirements, MatchResult, Skill

SYSTEM = """너는 요구 기술 하나에 대해 포트폴리오에서 근거를 찾는 매처다.
규칙:
- <portfolio> 안에 실제로 적힌 내용만 근거로 쓴다. 없는 경험을 만들어 내지 않는다.
- project 는 '## 프로젝트: 이름' 헤더의 이름을 그대로 쓴다.
- evidence 는 해당 프로젝트 문서에서 그대로 복사한 문장(또는 일부)이어야 한다.
- strength: 요구 기술을 직접 사용한 경험이 있으면 strong, 비슷하거나 일부만 해당하면 partial,
  근거가 없으면 none (이때 evidences 는 빈 목록).
"""


def match_skill(skill: Skill, projects: dict[str, str]) -> MatchResult:
    prompt = (
        f"{wrap_untrusted('portfolio', portfolio_as_text(projects))}\n\n"
        f"요구 기술: {skill.name} ({skill.kind})\n"
        f"공고 근거 문장: {skill.evidence_quote}\n\n"
        "이 기술에 대해 포트폴리오에서 근거를 찾아 판정하라."
    )
    result = generate_structured(
        step=f"match:{skill.name}",
        prompt=prompt,
        schema=MatchResult,
        system=SYSTEM,
    )

    # 코드 검증: 존재하는 프로젝트이고, 근거 문장이 그 프로젝트 문서에 있어야 한다
    good = []
    for ev in result.evidences:
        doc = projects.get(ev.project)
        if doc is not None and is_grounded(ev.evidence, doc):
            good.append(ev)

    if len(good) != len(result.evidences):
        log_event(
            "match_verify",
            skill=skill.name,
            status="dropped_ungrounded",
            dropped=len(result.evidences) - len(good),
        )

    result.skill = skill.name  # 이름은 공고 기준으로 고정
    result.evidences = good
    if not good:
        result.strength = "none"
    return result


def match_all(
    requirements: JobRequirements,
    projects: dict[str, str],
    max_workers: int = 3,  # 무료 티어 분당 호출 제한을 고려해 작게 유지
) -> list[MatchResult]:
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(lambda s: match_skill(s, projects), requirements.skills))