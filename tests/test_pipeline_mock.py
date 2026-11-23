"""LLM 호출 없이 파이프라인 흐름을 검증하는 테스트.

실행: python -m unittest discover -s tests -v   (프로젝트 루트에서)
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitcheck.pipeline import run_pipeline  # noqa: E402
from fitcheck.schemas import (  # noqa: E402
    FitReport,
    JobRequirements,
    MatchResult,
    ProjectEvidence,
    Skill,
)

JD = "자격 요건: Python 기반 개발 경험. 우대: Docker 배포 경험."
PROJECTS = {"study-planner": "Python Flask로 REST API를 설계하고 개발했다."}

REQ = JobRequirements(
    company="가상테크",
    position="AI 개발자",
    skills=[
        Skill(name="Python", kind="required", evidence_quote="Python 기반 개발 경험"),
        Skill(name="Docker", kind="preferred", evidence_quote="Docker 배포 경험"),
    ],
    responsibilities=[],
)


def fake_match(step, prompt, schema, system, **kw):
    name = step.split(":", 1)[1]
    if name == "Python":  # 정상 근거
        return MatchResult(
            skill="Python",
            strength="strong",
            evidences=[ProjectEvidence(project="study-planner", evidence="Python Flask로 REST API를 설계하고 개발했다")],
        )
    # Docker: 문서에 없는 근거를 지어냄 → 코드 검증에서 제거되어야 한다
    return MatchResult(
        skill="Docker",
        strength="strong",
        evidences=[ProjectEvidence(project="study-planner", evidence="Docker로 배포했다")],
    )


GOOD = FitReport(fit_level="medium", strengths=["Python 경험"], gaps=["Docker 경험 없음"],
                 suggestions=["Docker 실습"], sources=["Python Flask로 REST API를 설계하고 개발했다"])
BAD = FitReport(fit_level="high", strengths=["Docker 경험"], gaps=[],
                suggestions=[], sources=["Docker로 대규모 배포를 운영했다"])


class PipelineTest(unittest.TestCase):
    def _run(self, eval_results):
        with patch("fitcheck.extract.generate_structured", return_value=REQ), \
             patch("fitcheck.match.generate_structured", side_effect=fake_match), \
             patch("fitcheck.evaluate.generate_structured", side_effect=eval_results) as ev:
            return run_pipeline(JD, PROJECTS), ev

    def test_happy_path_and_ungrounded_match_is_dropped(self):
        result, ev = self._run([GOOD])
        self.assertTrue(result.verified)
        self.assertEqual(ev.call_count, 1)
        docker = next(m for m in result.matches if m.skill == "Docker")
        self.assertEqual(docker.strength, "none")  # 지어낸 근거 제거 → none
        self.assertEqual(docker.evidences, [])

    def test_regenerate_once_then_pass(self):
        result, ev = self._run([BAD, GOOD])
        self.assertTrue(result.verified)
        self.assertEqual(ev.call_count, 2)

    def test_regenerate_fails_drops_sources(self):
        result, ev = self._run([BAD, BAD])
        self.assertFalse(result.verified)
        self.assertEqual(ev.call_count, 2)  # max_regen=1 이므로 총 2회
        self.assertEqual(result.report.sources, [])
        self.assertTrue(result.dropped_sources)


if __name__ == "__main__":
    unittest.main()