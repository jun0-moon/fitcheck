"""포트폴리오 문서(data/portfolio/*.md) 로딩."""
from pathlib import Path


def load_portfolio(directory: str = "data/portfolio") -> dict[str, str]:
    """프로젝트 이름(파일명) → 문서 내용."""
    files = sorted(Path(directory).glob("*.md"))
    if not files:
        raise FileNotFoundError(f"{directory} 에 .md 포트폴리오 문서가 없습니다.")
    return {p.stem: p.read_text(encoding="utf-8") for p in files}


def portfolio_as_text(projects: dict[str, str]) -> str:
    """프로젝트들을 하나의 텍스트로 합친다. 프로젝트 이름을 헤더로 붙인다."""
    return "\n\n".join(f"## 프로젝트: {name}\n{text}" for name, text in projects.items())