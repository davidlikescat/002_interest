# 004 Google News AI 자동화 프로젝트

## 📖 프로젝트 개요

Google News를 활용한 실시간 AI 뉴스 자동화 시스템입니다. RSS 피드 대신 Google News를 직접 검색하여 **최신성을 극대화**했습니다.

### 🆕 주요 특징
- **실시간 검색**: Google News Korea에서 실시간 검색
- **최신성 우선**: 최근 24시간 이내 기사만 수집
- **고정 수량**: 품질 높은 5개 기사만 선별
- **AI 필터링**: 키워드 기반 정교한 필터링
- **완전 자동화**: 수집 → 크롤링 → 요약 → 저장 → 알림

## 🔄 프로세스 플로우

```
Google News 검색 → 최신 기사 수집 → 본문 크롤링 → AI 요약 → Notion 저장 → Telegram 알림
```

## 📂 프로젝트 구조

```
004_google_news_ai/
├── main.py                    # 메인 실행 파일
├── config.py                  # 설정 관리
├── google_news_collector.py   # Google News 수집기 (신규)
├── article_crawler.py         # 기사 크롤링
├── ai_summarizer.py          # AI 요약 생성
├── artifact_generator.py     # 리포트 생성
├── notion_saver.py           # Notion 저장
├── telegram_sender.py        # Telegram 전송
├── requirements.txt          # 의존성
├── .env                      # 환경 변수
└── README.md                 # 이 파일
```

## 🚀 설치 및 설정

### 1. 프로젝트 설치
```bash
# 프로젝트 폴더 생성
mkdir 004_google_news_ai
cd 004_google_news_ai

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일 생성 후 다음 내용 입력:

```env
# OpenAI API 설정
OPENAI_API_KEY=your_openai_api_key_here

# Notion API 설정
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_notion_database_id_here

# Telegram Bot 설정
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# 추가 설정 (선택사항)
DEBUG_MODE=False
AI_MODEL=gpt-3.5-turbo
```

### 3. API 키 발급 가이드
- **OpenAI API**: https://platform.openai.com/api-keys
- **Notion API**: https://www.notion.so/my-integrations
- **Telegram Bot**: @BotFather에서 봇 생성

## 💻 사용법

### 기본 실행
```bash
python main.py
```

### 시스템 테스트
```bash
python main.py test
```

### 환경 설정 도우미
```bash
python main.py setup
```

## 🎯 Google News 검색 최적화

### 핵심 검색 키워드 (10개)
- 인공지능, AI, 생성형AI, ChatGPT, LLM
- 네이버, 카카오, 삼성, 자율주행, AI반도체

### 수집 조건
- **시간 범위**: 최근 24시간 이내
- **지역**: 한국 (Google News Korea)
- **언어**: 한국어 우선
- **최대 수량**: 5개 (고정)

## 📊 결과물

### 1. Notion 데이터베이스
- 제목, 요약, 키워드, 카테고리
- 발행 시간, 출처, 원문 링크
- AI 생성 태그 및 분류

### 2. Telegram 알림
```
🎯 Google News AI 리포트
[📄 상세 뉴스 보기](notion_url)

🔑 주요 키워드
#인공지능 #AI #생성형AI #ChatGPT #네이버 #카카오

⏰ 수집 정보
• 수집 시각: 2025-06-03 15:30
• 수집 기사: 5개 (최신 24시간 이내)
• 데이터 소스: Google News Korea

🤖 시스템 정보
- 시스템: Google News AI 자동화 에이전트 v2.00
- 프로젝트: 004
```

## 🔧 커스터마이징

### 검색 키워드 수정
`config.py`의 `CORE_SEARCH_KEYWORDS` 수정:

```python
CORE_SEARCH_KEYWORDS = [
    '인공지능', 'AI', '생성형AI', 'ChatGPT', 'LLM',
    # 추가 키워드...
]
```

### 수집 조건 변경
```python
MAX_ARTICLES = 5        # 최대 기사 수
SEARCH_HOURS = 24       # 검색 시간 범위 (시간)
REQUEST_DELAY = 0.5     # 요청 간 딜레이 (초)
```

## 📈 성능 최적화

### Google News 접근 최적화
- User-Agent 최적화
- 요청 간 딜레이 설정
- 한국 지역/언어 설정
- RSS 피드 활용

### 크롤링 효율성
- 병렬 처리 지원
- 재시도 로직
- 타임아웃 설정
- 에러 핸들링

## 🚨 주의사항

1. **API 사용량**: OpenAI API 사용량 모니터링 필요
2. **요청 제한**: Google News 과도한 요청 주의
3. **에러 처리**: 네트워크 오류 대응
4. **데이터 품질**: AI 키워드 기반 필터링 활용

## 📋 로그 및 모니터링

### 로그 파일
- `google_news_agent.log`: 시스템 실행 로그
- 실시간 콘솔 출력

### 모니터링 포인트
- 수집 성공률
- 크롤링 성공률
- AI 요약 품질
- Notion 저장 상태
- Telegram 전송 상태

## 🔄 업데이트 내역

### v2.00 (004 프로젝트)
- RSS 피드 → Google News 검색으로 변경
- 최신성 중심의 수집 방식
- 고정 5개 기사 수집
- 검색 키워드 최적화
- 프로젝트 코드 체계 도입

## 👨‍💻 개발자 정보

- **개발자**: 양준모
- **이메일**: davidlikescat@icloud.com
- **프로젝트**: 004 Google News AI 자동화
- **버전**: v2.00

## 📄 라이센스

© 2025 양준모. Google News AI 자동화 시스템. All rights reserved.