# Google News AI Agent v1.5 - 개발 문서

## 📋 목차
- [프로젝트 개요](#프로젝트-개요)
- [시스템 아키텍처](#시스템-아키텍처)
- [기술 스택](#기술-스택)
- [파일 구조](#파일-구조)
- [설치 및 설정](#설치-및-설정)
- [API 설정](#api-설정)
- [개발 가이드](#개발-가이드)
- [배포 가이드](#배포-가이드)
- [트러블슈팅](#트러블슈팅)
- [API 참조](#api-참조)

## 🚀 프로젝트 개요

### 프로젝트 정보
- **프로젝트명**: Google News AI Agent v1.5
- **개발자**: Joonmo Yang
- **이메일**: davidlikescat@icloud.com
- **라이선스**: All rights reserved
- **개발 기간**: 2024-2025
- **버전**: v1.5 (Simplified Architecture)

### 주요 기능
1. **AI 뉴스 자동 수집**: Google News RSS를 통한 실시간 AI 뉴스 수집
2. **스마트 키워드 필터링**: Google Sheets 기반 동적 키워드 관리
3. **자동 크롤링**: BeautifulSoup4를 이용한 기사 본문 추출
4. **Notion 저장**: 수집된 뉴스를 구조화된 Notion 페이지로 저장
5. **Telegram 알림**: 수집 완료 시 실시간 알림 전송
6. **스케줄러**: 매일 자동 실행 (07:30 KST)
7. **비용 효율성**: OpenAI API 비용 없이 운영

### 시스템 특징
- **Zero OpenAI Cost**: OpenAI API 없이 순수 RSS + 크롤링 방식
- **Cloud Ready**: GCP Compute Engine 배포 지원
- **Docker Support**: 컨테이너 기반 배포
- **Systemd Integration**: 시스템 서비스 등록 지원
- **Error Resilience**: 강력한 에러 처리 및 복구 메커니즘

## 🏗️ 시스템 아키텍처

### 전체 플로우
```
Google News RSS → 키워드 필터링 → 기사 크롤링 → Notion 저장 → Telegram 알림
```

### 컴포넌트 다이어그램
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   main.py       │    │ keyword_manager │    │ news_collector  │
│   (Entry Point) │───▶│ (Google Sheets) │───▶│ (RSS + Crawl)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         ▼                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   config.py     │    │ storage_manager │    │   notifier.py   │
│   (Settings)    │    │ (Notion API)    │    │ (Telegram Bot)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 데이터 플로우
1. **키워드 로딩**: Google Sheets에서 동적 키워드 로드 (캐시 5분)
2. **뉴스 검색**: Google News RSS API 호출
3. **필터링**: 키워드 매칭으로 관련 기사 선별
4. **크롤링**: 각 기사의 본문 내용 추출
5. **저장**: Notion 데이터베이스에 구조화된 페이지 생성
6. **알림**: Telegram으로 수집 결과 전송

## 🛠️ 기술 스택

### Core Technologies
- **언어**: Python 3.9+
- **웹 크롤링**: BeautifulSoup4, requests, lxml
- **RSS 파싱**: feedparser
- **스케줄링**: schedule
- **환경 관리**: python-dotenv

### External APIs
- **Google News RSS**: 뉴스 데이터 소스
- **Google Sheets API**: 동적 키워드 관리
- **Notion API**: 데이터 저장
- **Telegram Bot API**: 알림 전송

### Infrastructure
- **클라우드**: Google Cloud Platform (Compute Engine)
- **컨테이너**: Docker, Docker Compose
- **프로세스 관리**: systemd
- **버전 관리**: Git, GitHub

### Development Tools
- **에디터**: Claude Code, VS Code
- **디버깅**: Python logging, journalctl
- **모니터링**: systemctl, GCP Console

## 📁 파일 구조

### Core Files (운영 필수)
```
004_google_news/
├── main.py                    # 🔥 메인 실행 파일
├── news_collector.py          # 📰 뉴스 수집 + 크롤링
├── keyword_manager.py         # 🔑 Google Sheets 키워드 관리
├── storage_manager.py         # 💾 Notion 저장 관리
├── notifier.py               # 📱 Telegram 알림
├── config.py                 # ⚙️ 시스템 설정
├── requirements.txt          # 📦 의존성 패키지
└── .env                      # 🔑 환경변수 (보안)
```

### Deployment Files
```
├── Dockerfile                # 🐳 Docker 이미지 설정
├── docker-compose.yml        # 🐳 Docker Compose 구성
├── google-news-ai.service    # ⚙️ systemd 서비스 설정
├── run.sh                    # 🚀 실행 스크립트
├── .gitignore               # 📝 Git 제외 파일
└── .env.example             # 📋 환경변수 템플릿
```

### Documentation
```
├── README.md                # 📖 사용자 가이드
├── DEV_DOCS.md             # 🔧 개발자 문서 (이 파일)
└── old_system/             # 📁 레거시 파일 보관
```

### Google Sheets Credentials
```
├── credentials.json         # 🔐 Google Sheets API 키
└── credential.json         # 🔐 백업 인증 파일
```

## ⚙️ 설치 및 설정

### 1. 환경 준비
```bash
# Python 3.9+ 설치 확인
python3 --version

# 프로젝트 클론
git clone https://github.com/davidlikescat/002_interest.git
cd 002_interest

# 의존성 설치
pip3 install -r requirements.txt
```

### 2. 환경변수 설정
```bash
# 환경변수 파일 생성
cp .env.example .env

# 필수 환경변수 설정 (4개)
vim .env
```

필수 환경변수:
```env
# Notion API
NOTION_API_KEY=ntn_your_notion_api_key
NOTION_DATABASE_ID=your_database_id

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 3. Google Sheets 설정 (선택사항)
```bash
# Google Cloud Console에서 서비스 계정 생성
# credentials.json 다운로드 후 프로젝트 루트에 배치

# 스프레드시트 생성 및 서비스 계정에 편집 권한 부여
python3 keyword_manager.py setup
```

## 🔑 API 설정

### Notion API 설정
1. [Notion Developers](https://developers.notion.com/) 접속
2. "Create new integration" 클릭
3. API 키 복사 → `NOTION_API_KEY`
4. 데이터베이스 생성 후 integration과 공유
5. 데이터베이스 URL에서 ID 추출 → `NOTION_DATABASE_ID`

### Telegram Bot 설정
1. Telegram에서 @BotFather 검색
2. `/newbot` 명령어로 봇 생성
3. Bot Token 복사 → `TELEGRAM_BOT_TOKEN`
4. 봇과 대화 시작
5. `https://api.telegram.org/bot<TOKEN>/getUpdates`에서 Chat ID 확인 → `TELEGRAM_CHAT_ID`

### Google Sheets API 설정 (선택)
1. Google Cloud Console에서 프로젝트 생성
2. Google Sheets API + Google Drive API 활성화
3. 서비스 계정 생성 후 JSON 키 다운로드
4. `credentials.json`으로 저장
5. 스프레드시트 생성 후 서비스 계정에 편집 권한 부여

## 💻 개발 가이드

### 로컬 개발 환경
```bash
# 설정 확인
python3 config.py

# 개별 컴포넌트 테스트
python3 keyword_manager.py test
python3 storage_manager.py
python3 notifier.py

# 전체 시스템 테스트
python3 main.py test

# 단일 실행
python3 main.py
```

### 디버깅
```bash
# 로그 확인
tail -f news_agent.log

# 상세 로그 활성화 (config.py에서)
LOG_LEVEL = "DEBUG"

# 컴포넌트별 테스트
python3 -c "from storage_manager import StorageManager; StorageManager().test_connection()"
```

### 코드 수정 가이드

#### 1. 키워드 추가/수정
```python
# keyword_manager.py에서 기본 키워드 수정
DEFAULT_KEYWORDS = [
    "인공지능", "AI", "생성형AI",
    "ChatGPT", "LLM", "GPT",
    # 새 키워드 추가
]
```

#### 2. 수집 기사 수 변경
```python
# config.py에서
MAX_ARTICLES = 20  # 기본값: 10
```

#### 3. 스케줄 시간 변경
```python
# config.py에서
SCHEDULE_TIME = "09:00"  # 기본값: "07:30"
```

#### 4. Telegram 메시지 포맷 수정
```python
# notifier.py의 _build_success_message() 메서드 수정
```

### 새로운 기능 추가

#### 1. 새로운 뉴스 소스 추가
```python
# news_collector.py에서 _fetch_google_news() 메서드 확장
def _fetch_additional_source(self, keywords):
    # 새 RSS 소스 구현
    pass
```

#### 2. 새로운 저장 백엔드 추가
```python
# 새 파일: database_manager.py
class DatabaseManager:
    def save_articles(self, articles):
        # PostgreSQL, MongoDB 등 구현
        pass
```

## 🚀 배포 가이드

### Docker 배포
```bash
# 이미지 빌드
docker build -t google-news-ai .

# Docker Compose 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### GCP 배포
```bash
# 서버 접속
gcloud compute ssh discord-youtube-bot --zone=asia-northeast3-a --project=n8n-ai-work-agent-automation

# 저장소 클론
git clone https://github.com/davidlikescat/002_interest.git
cd 002_interest

# 환경 설정
cp .env.example .env
# .env 파일 편집 후

# 의존성 설치
pip3 install -r requirements.txt

# 시스템 서비스 등록
sudo cp google-news-ai.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable google-news-ai
sudo systemctl start google-news-ai

# 서비스 상태 확인
sudo systemctl status google-news-ai
```

### 서비스 관리
```bash
# 서비스 시작/중지/재시작
sudo systemctl start google-news-ai
sudo systemctl stop google-news-ai
sudo systemctl restart google-news-ai

# 로그 확인
sudo journalctl -u google-news-ai -f

# 자동 시작 설정
sudo systemctl enable google-news-ai
```

## 🔧 트러블슈팅

### 일반적인 문제

#### 1. 환경변수 로딩 실패
```bash
# 증상: "API 설정이 누락되었습니다"
# 해결: .env 파일 존재 및 권한 확인
ls -la .env
cat .env | grep NOTION_API_KEY
```

#### 2. Notion 연결 실패
```bash
# 증상: "Notion 연결 실패: 401"
# 해결: API 키 및 데이터베이스 권한 확인
python3 -c "from storage_manager import StorageManager; StorageManager().test_connection()"
```

#### 3. Google Sheets 인증 실패
```bash
# 증상: "Google Sheets 인증 파일을 찾을 수 없습니다"
# 해결: credentials.json 파일 확인
ls -la credentials.json
python3 keyword_manager.py test
```

#### 4. Telegram 알림 실패
```bash
# 증상: "Telegram 전송 실패"
# 해결: Bot Token 및 Chat ID 확인
python3 notifier.py
```

### 성능 최적화

#### 1. 크롤링 속도 개선
```python
# config.py에서 요청 지연 시간 조정
REQUEST_DELAY = 0.5  # 기본값: 1.0초
```

#### 2. 메모리 사용량 최적화
```python
# news_collector.py에서 배치 크기 조정
BATCH_SIZE = 5  # 기본값: 10
```

#### 3. 캐시 설정 최적화
```python
# keyword_manager.py에서
CACHE_DURATION = 600  # 10분 (기본값: 300초)
```

### 로그 분석

#### 중요한 로그 패턴
```bash
# 성공적인 실행
grep "AI 뉴스 수집 완료" news_agent.log

# 에러 패턴 확인
grep "ERROR" news_agent.log

# 성능 모니터링
grep "완료.*초" news_agent.log
```

## 📖 API 참조

### Config 클래스
```python
from config import Config

# 설정 확인
Config.validate_config()

# 한국 시간 조회
korea_time = Config.get_korea_time()

# 설정 정보 출력
Config.print_config()
```

### KeywordManager 클래스
```python
from keyword_manager import KeywordManager

# 키워드 매니저 초기화
km = KeywordManager()

# 키워드 로드
keywords = km.get_keywords()

# 통계 업데이트
km.update_usage_stats(keyword, article_count)

# 연결 테스트
km.test_connection()
```

### NewsCollector 클래스
```python
from news_collector import NewsCollector

# 뉴스 수집기 초기화
collector = NewsCollector()

# AI 뉴스 수집
articles = collector.collect_ai_news(max_articles=10)

# 수집 통계 조회
stats = collector.get_collection_stats()
```

### StorageManager 클래스
```python
from storage_manager import StorageManager

# 저장 매니저 초기화
storage = StorageManager()

# Notion에 저장
notion_url = storage.save_news_to_notion(articles)

# 연결 테스트
storage.test_connection()
```

### Notifier 클래스
```python
from notifier import Notifier

# 알림 시스템 초기화
notifier = Notifier()

# 성공 알림 전송
notifier.send_success_notification(articles, notion_url)

# 에러 알림 전송
notifier.send_error_notification("에러 메시지")

# 연결 테스트
notifier.test_connection()
```

## 📊 성능 지표

### 시스템 성능
- **평균 실행 시간**: 120-150초 (10개 기사)
- **메모리 사용량**: ~100MB
- **네트워크 요청**: ~30-50회
- **CPU 사용률**: 낮음 (I/O 바운드)

### API 호출 제한
- **Google News RSS**: 제한 없음
- **Notion API**: 3 requests/second
- **Telegram Bot API**: 30 requests/second
- **Google Sheets API**: 100 requests/100초

### 비용 분석
- **OpenAI API**: $0 (사용 안함)
- **Google Sheets API**: 무료 (100만 요청/월)
- **Notion API**: 무료
- **Telegram Bot API**: 무료
- **GCP Compute Engine**: ~$10-20/월

## 🔮 향후 계획

### v1.6 계획
- [ ] Google Trends API 통합 (자동 키워드 발견)
- [ ] 멀티 언어 뉴스 지원
- [ ] 웹 대시보드 추가
- [ ] 성능 모니터링 대시보드
- [ ] 더 많은 뉴스 소스 지원

### v2.0 계획
- [ ] AI 기반 기사 요약
- [ ] 감정 분석 및 트렌드 분석
- [ ] 실시간 뉴스 스트리밍
- [ ] 마이크로서비스 아키텍처 전환
- [ ] Kubernetes 배포 지원

## 👨‍💻 개발자 정보

**개발자**: Joonmo Yang
**이메일**: davidlikescat@icloud.com
**시스템**: Google News Crawler v1.5
**라이선스**: © 2025 Joonmo Yang. Google News AI Automation. All rights reserved.

### 기여 방법
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### 문의 및 지원
- **이메일**: davidlikescat@icloud.com
- **GitHub Issues**: Repository issues 탭 활용
- **개발 문의**: 이메일로 연락

---

📝 **문서 업데이트**: 2025-09-20
🔄 **문서 버전**: v1.0
📋 **마지막 검토**: Joonmo Yang