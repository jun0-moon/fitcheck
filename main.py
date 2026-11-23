"""FitCheck 실행 진입점.

사용법:
  python main.py data/sample_jd.txt
  python main.py data/sample_jd_injection.txt --out reports/injection.md
"""
import argparse
from pathlib import Path

from fitcheck.pipeline import run_pipeline
from fitcheck.portfolio import load_portfolio
from fitcheck.report import render_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="채용공고와 포트폴리오의 적합도를 점검한다.")
    parser.add_argument("jd", help="채용공고 텍스트 파일 경로")
    parser.add_argument("--portfolio", default="data/portfolio", help="포트폴리오 폴더")
    parser.add_argument("--out", default="reports/report.md", help="리포트 저장 경로")
    args = parser.parse_args()

    jd_text = Path(args.jd).read_text(encoding="utf-8")
    projects = load_portfolio(args.portfolio)

    result = run_pipeline(jd_text, projects)
    markdown = render_markdown(result)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown, encoding="utf-8")

    print(markdown)
    print(f"리포트 저장: {out}")


if __name__ == "__main__":
    main()