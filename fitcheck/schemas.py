"""단계 사이에서 주고받는 데이터 계약(JSON 스키마).

자연어 요약 대신 이 구조만 넘겨서 정보 누락(전화 게임)을 막는다.
"""
from typing import Literal

from pydantic import BaseModel, Field


class Skill(BaseModel):
    name: str = Field(description="기술 또는 역량 이름. 예: Python")
    kind: Literal["required", "preferred"] = Field(
        description="필수(required) 또는 우대(preferred)"
    )
    evidence_quote: str = Field(description="공고 원문에서 그대로 가져온 근거 문장")


class JobRequirements(BaseModel):
    company: str
    position: str
    skills: list[Skill]
    responsibilities: list[str]


class ProjectEvidence(BaseModel):
    project: str = Field(description="포트폴리오에 있는 프로젝트 이름")
    evidence: str = Field(description="포트폴리오 문서에서 그대로 가져온 근거 문장")


class MatchResult(BaseModel):
    skill: str
    strength: Literal["strong", "partial", "none"]
    evidences: list[ProjectEvidence] = Field(
        description="strength가 none이면 빈 목록. 문서에 없는 내용은 절대 쓰지 않는다",
    )


class FitReport(BaseModel):
    fit_level: Literal["high", "medium", "low"]
    strengths: list[str]
    gaps: list[str]
    suggestions: list[str]
    sources: list[str] = Field(description="주장의 근거가 된 프로젝트·문장")