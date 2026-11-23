"""1단계: 채용공고 텍스트 → JobRequirements(JSON).

LLM이 뽑은 결과를 그대로 믿지 않고, 코드로 한 번 더 검증한다.
- evidence_quote 가 공고 원문에 실제로 존재하는가? (없으면 환각으로 보고 제외)
"""
import re

from .llm import generate_structured, log_event, wrap_untrusted
from .schemas import JobRequirements

SYSTEM = """너는 채용공고에서 요구사항을 추출하는 분석기다.
규칙:
- 공고에 적힌 내용만 추출한다. 공고에 없는 기술을 추가하거나 추측하지 않는다.
- 각 skill의 evidence_quote 는 공고 원문에서 그대로 복사한 문장(또는 문장의 일부)이어야 한다.
- 자격요건/필수 항목은 required, 우대사항은 preferred 로 분류한다.
- 회사명이나 직무명이 공고에 없으면 "unknown" 으로 쓴다.
"""


def _normalize(text: str) -> str:
    """공백·줄바꿈 차이를 무시하고 비교하기 위한 정규화."""
    return re.sub(r"\s+", "", text).lower()


def is_grounded(quote: str, source: str) -> bool:
    """quote 가 원문(source)에 실제로 들어 있는지 확인한다."""
    q = _normalize(quote)
    return bool(q) and q in _normalize(source)


def extract_requirements(jd_text: str) -> JobRequirements:
    prompt = (
        f"{wrap_untrusted('job_posting', jd_text)}\n\n"
        "위 공고에서 회사명, 직무명, 요구 기술(필수/우대), 주요 업무를 추출하라."
    )
    result = generate_structured(
        step="extract",
        prompt=prompt,
        schema=JobRequirements,
        system=SYSTEM,
    )

    # 코드 검증: 공고 원문에 근거가 없는 skill 은 제외하고 기록한다
    kept, dropped = [], []
    for skill in result.skills:
        (kept if is_grounded(skill.evidence_quote, jd_text) else dropped).append(skill)

    if dropped:
        log_event(
            "extract_verify",
            status="dropped_ungrounded",
            dropped=[s.name for s in dropped],
        )
    result.skills = kept
    return result