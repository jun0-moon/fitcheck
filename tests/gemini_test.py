"""모델별 응답 속도와 구조화된 출력이 되는지 확인한다.

프로젝트 루트에서 실행:
  python scripts/check_models.py
  python scripts/check_models.py gemini-3.1-flash-lite gemini-2.5-flash   # 모델 직접 지정

실제 extract 단계와 같은 요청(공고 + JobRequirements 스키마)을 모델마다 1번씩 보낸다.
모델별 무료 한도가 따로 계산되므로 1번씩은 한도에 걸리지 않는다.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv  # noqa: E402
from google import genai  # noqa: E402
from google.genai import types  # noqa: E402

from fitcheck.schemas import JobRequirements  # noqa: E402

load_dotenv()

DEFAULT_MODELS = [
    "gemini-4-hydrogen",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash",
]
models = sys.argv[1:] or DEFAULT_MODELS

jd = Path("data/sample_jd.txt").read_text(encoding="utf-8")
prompt = (
    f"<job_posting>\n{jd}\n</job_posting>\n\n"
    "위 공고에서 회사명, 직무명, 요구 기술(필수/우대), 주요 업무를 추출하라."
)

client = genai.Client(
    http_options=types.HttpOptions(
        timeout=120_000,
        retry_options=types.HttpRetryOptions(attempts=1),
    )
)

for model in models:
    start = time.time()
    try:
        resp = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JobRequirements,
            ),
        )
        data = JobRequirements.model_validate_json(resp.text)
        print(f"OK   {model:24s} {time.time() - start:6.1f}s  skills={len(data.skills)}", flush=True)
    except Exception as e:
        print(
            f"FAIL {model:24s} {time.time() - start:6.1f}s  {type(e).__name__}: {str(e)[:120]}",
            flush=True,
        )