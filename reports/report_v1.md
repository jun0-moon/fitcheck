# FitCheck 리포트: 가상테크 / AI 서비스 개발자

**적합도: 보통**

## 요구 기술 매칭

| 기술 | 구분 | 매칭 | 근거 프로젝트 |
|---|---|---|---|
| Python | 필수 | 강함 | campus-chatbot, study-planner |
| REST API | 필수 | 강함 | study-planner |
| Git | 필수 | 부분 | study-planner |
| LLM API | 우대 | 강함 | campus-chatbot |
| 벡터 DB | 우대 | 없음 | - |
| Docker | 우대 | 없음 | - |
| 클라우드 배포 | 우대 | 부분 | algo-visualizer |

## 강점

- Python을 활용한 웹 서비스 개발 및 API 연동 경험
- Flask를 활용한 REST API 설계 및 개발 역량 보유
- Gemini API를 이용한 문서 요약 및 질의응답 서비스 구현 경험

## 부족한 점

- 벡터 DB 및 임베딩 검색 경험 부재
- Docker를 활용한 컨테이너화 경험 부족
- 클라우드 인프라 배포 경험이 GitHub Pages로 한정됨
- Git 협업 경험이 부분적임

## 보완 제안

- ChromaDB나 FAISS 등 벡터 DB를 활용한 간단한 RAG(검색 증강 생성) 프로젝트를 수행하여 기술적 공백을 메울 것
- 기존 Python 프로젝트를 Docker 컨테이너로 패키징하고, AWS나 GCP 등 클라우드 환경에 배포하는 실습 진행
- Git 활용 시 워크플로우를 더욱 고도화하여 협업 역량을 증명할 수 있는 구체적인 프로젝트 경험 추가

## 근거 (포트폴리오 원문)

- Gemini API를 호출해 공지 내용을 요약하고 질문에 답하는 기능을 Python으로 구현했다.
- Python Flask로 REST API를 설계하고 개발했다.
- 팀원 3명과 GitHub에서 브랜치 전략을 정해 Pull Request 기반으로 협업했다.
- GitHub Pages로 배포했다.

## 검증 결과

- 통과: 모든 근거가 포트폴리오 원문에서 확인되었습니다.
