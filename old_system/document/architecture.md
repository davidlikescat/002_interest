# Google News AI 자동화 시스템 아키텍처

## 시스템 개요
이 시스템은 구글 뉴스를 자동으로 수집하고, AI를 활용하여 요약하여 노션에 저장하고 텔레그램으로 알림을 보내는 자동화 시스템입니다.

## 주요 구성요소 및 역할

### 1. 메인 구성요소
- `main.py`: 전체 시스템의 메인 실행 파일
- `config.py`: 시스템 설정 및 환경 변수 관리
- `.env`: 환경 변수 설정 파일
- `credential.json`: 구글 API 인증 정보

### 2. 핵심 모듈

#### 뉴스 수집 및 크롤링
- `google_news_collector.py`: 구글 뉴스 수집
  - 키워드 기반 뉴스 검색
  - 뉴스 URL 수집
- `article_crawler.py`: 기사 크롤링
  - 수집된 URL의 기사 내용 수집
  - 기사 메타데이터 추출

#### 데이터 처리
- `ai_summarizer.py`: AI 요약
  - OpenAI API를 활용한 기사 요약
  - 키워드 추출
- `keyword_manager.py`: 키워드 관리
  - 키워드 데이터베이스 관리
  - 키워드 분석 및 업데이트

#### 데이터 저장 및 관리
- `notion_saver.py`: 노션 저장
  - 노션 데이터베이스 연동
  - 기사 정보 저장 및 관리
- `google_sheets_manager.py`: 구글 시트 관리
  - 키워드 관리 시트
  - 수집 결과 시트

#### 자동화 및 스케줄링
- `scheduler.py`: 스케줄링 관리
  - 주기적인 작업 실행
  - 작업 상태 모니터링

### 3. 워크플로우

1. **뉴스 수집 단계**
   - `google_news_collector.py` 실행
   - 키워드 기반 구글 뉴스 검색
   - 뉴스 URL 수집

2. **기사 크롤링 단계**
   - `article_crawler.py` 실행
   - 수집된 URL의 기사 내용 수집
   - 메타데이터 추출

3. **AI 처리 단계**
   - `ai_summarizer.py` 실행
   - 기사 요약 생성
   - 키워드 추출

4. **데이터 저장 단계**
   - `notion_saver.py` 실행
   - 노션 데이터베이스에 저장
   - 구글 시트 업데이트

5. **알림 단계**
   - 텔레그램 알림 전송
   - 수집 결과 공유

### 4. 설정 및 환경

#### 환경 변수 (.env)
- API 키 (OpenAI, Telegram, Google API)
- 노션 토큰
- 구글 시트 ID
- 텔레그램 채널 ID

#### 의존성 패키지 (requirements.txt)
- requests: HTTP 요청 처리
- beautifulsoup4: HTML 파싱
- openai: AI 서비스
- gspread: 구글 시트 연동
- notion-client: 노션 연동
- schedule: 스케줄링

## 시스템 특징

1. **모듈화된 구조**
   - 각 기능별로 독립적인 모듈로 구성
   - 모듈 간 의존성 최소화
   - 유지보수 및 확장성 향상

2. **자동화**
   - 주기적인 뉴스 수집
   - 자동 요약 생성
   - 자동 저장 및 알림

3. **확장성**
   - 새로운 데이터 소스 추가 가능
   - 추가 AI 서비스 통합 가능
   - 다양한 알림 채널 지원

## 실행 방법

1. 환경 설정
   ```bash
   cp .env.example .env  # 환경 변수 설정
   pip install -r requirements.txt  # 의존성 설치
   ```

2. 실행
   ```bash
   python main.py  # 전체 시스템 실행
   ```

3. 테스트 실행
   ```bash
   python google_news_collector.py  # 뉴스 수집 테스트
   python article_crawler.py        # 기사 크롤링 테스트
   python notion_saver.py           # 노션 저장 테스트
   ```
