#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google News 간단 수집 시스템 설정 (OpenAI 제외)
기사 수집 → Notion 저장 → Telegram 전송
"""

import os
from dotenv import load_dotenv

# .env 파일 로드 (GCP 환경 고려)
env_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print("⚠️ .env 파일을 찾을 수 없습니다. 환경 변수를 직접 확인합니다.")

class Config:
    """Google News 간단 수집 시스템 설정"""
    
    # 프로젝트 정보
    PROJECT_CODE = "004_google_news_simple"
    SYSTEM_NAME = "Google News 자동화 에이전트"
    SYSTEM_VERSION = "v1.2"
    DEVELOPER_NAME = "양준모"
    DEVELOPER_EMAIL = "davidlikescat@icloud.com"
    
    # 뉴스 수집 설정
    MAX_ARTICLES = 10
    SEARCH_HOURS = 24
    
    # 검색 키워드
    AI_KEYWORDS = [
        "artificial intelligence",
        "AI",
        "machine learning",
        "deep learning", 
        "neural network",
        "ChatGPT",
        "OpenAI",
        "Google AI",
        "인공지능",
        "머신러닝",
        "딥러닝",
        "생성형 AI",
        "AI 기술"
    ]
    
    TECH_KEYWORDS = [
        "technology",
        "tech",
        "software",
        "programming",
        "developer",
        "기술",
        "소프트웨어", 
        "개발자",
        "IT",
        "스타트업"
    ]
    
    # API 키들 (OpenAI 제외)
    NOTION_API_KEY = os.getenv('NOTION_API_KEY')
    NOTION_TOKEN = NOTION_API_KEY  # 호환성을 위한 별칭
    NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
    NOTION_PAGE_ID = os.getenv('NOTION_PAGE_ID')
    
    # Telegram 설정
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # 스케줄 설정
    SCHEDULE_TIME = "07:30"  # 매일 오전 7시 30분
    TIMEZONE = "Asia/Seoul"
    
    # 크롤링 설정
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    
    # Google News 설정
    GOOGLE_NEWS_URL = "https://news.google.com/rss"
    NEWS_LANGUAGE = "ko"
    NEWS_COUNTRY = "KR"
    
    # 필터링 설정
    MIN_ARTICLE_LENGTH = 100
    MAX_ARTICLE_LENGTH = 10000
    
    # 로그 설정
    LOG_LEVEL = "INFO"
    LOG_FILE = "simple_news_collector.log"
    
    # 기타 설정
    DEBUG_MODE = False
    SAVE_RAW_DATA = False
    
    # 페이지 설정
    NOTION_PAGE_TITLE_PREFIX = "Google News"
    NOTION_PAGE_ICON = "🤖"
    
    # 알림 설정
    TELEGRAM_PARSE_MODE = "HTML"
    TELEGRAM_DISABLE_WEB_PAGE_PREVIEW = True
    
    @classmethod
    def get_search_keywords(cls):
        """AI 관련 검색 키워드 반환"""
        return cls.AI_KEYWORDS
    
    @classmethod
    def get_all_keywords(cls):
        """모든 검색 키워드 반환"""
        return cls.AI_KEYWORDS + cls.TECH_KEYWORDS
    
    @classmethod
    def get_headers(cls):
        """HTTP 요청 헤더 반환"""
        return {
            'User-Agent': cls.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    @classmethod
    def validate_config(cls):
        """필수 설정 검증 (OpenAI 제외)"""
        required_settings = {
            'NOTION_API_KEY': cls.NOTION_API_KEY, 
            'NOTION_DATABASE_ID': cls.NOTION_DATABASE_ID,
            'TELEGRAM_BOT_TOKEN': cls.TELEGRAM_BOT_TOKEN,
            'TELEGRAM_CHAT_ID': cls.TELEGRAM_CHAT_ID
        }
        
        missing = []
        for key, value in required_settings.items():
            if not value:
                missing.append(key)
        
        if missing:
            error_msg = f"필수 환경변수가 설정되지 않았습니다: {', '.join(missing)}"
            print(f"❌ {error_msg}")
            print("💡 GCP 환경 변수 설정을 확인하세요")
            raise ValueError(error_msg)
        
        print("✅ 설정 검증 완료 (OpenAI 불필요)")
        return True
    
    @classmethod
    def print_config(cls):
        """설정 정보 출력 (민감한 정보 제외)"""
        print(f"🔧 프로젝트: {cls.PROJECT_CODE}")
        print(f"⚙️ 시스템: {cls.SYSTEM_NAME} {cls.SYSTEM_VERSION}")
        print(f"👤 개발자: {cls.DEVELOPER_NAME}")
        print(f"📊 수집 기사 수: {cls.MAX_ARTICLES}개")
        print(f"⏰ 수집 범위: 최근 {cls.SEARCH_HOURS}시간")
        print(f"🕐 스케줄: 매일 {cls.SCHEDULE_TIME}")
        print(f"🔑 키워드 수: {len(cls.get_all_keywords())}개")
        
        # API 설정 상태 (OpenAI 제외)
        apis = {
            'Notion': bool(cls.NOTION_API_KEY and cls.NOTION_DATABASE_ID), 
            'Telegram': bool(cls.TELEGRAM_BOT_TOKEN and cls.TELEGRAM_CHAT_ID)
        }
        
        print("🔗 API 설정 상태:")
        for api, status in apis.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {api}")
        
        print("💡 특징: OpenAI API 불필요, 기사 원문 직접 수집")

def setup_environment():
    """환경 설정 가이드"""
    print("🔧 Google News 간단 수집 시스템 환경 설정")
    print("=" * 60)
    
    # .env 파일 예제 생성 (OpenAI 제외)
    env_example = """# Google News 간단 수집 시스템 환경변수
# OpenAI API가 필요하지 않습니다!

# Notion API
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_notion_database_id_here
NOTION_PAGE_ID=your_notion_page_id_here

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_example)
    
    print("📄 .env.example 파일이 생성되었습니다")
    print("🔑 Notion과 Telegram API 키만 .env 파일에 설정하세요")
    print("💡 OpenAI API 키는 필요하지 않습니다!")
    
    # 설정 상태 확인
    try:
        Config.validate_config()
    except ValueError as e:
        print(f"⚠️ {e}")
        print("💡 .env 파일을 확인하고 필요한 API 키를 설정하세요")

if __name__ == "__main__":
    print("📋 Google News 간단 수집 시스템 설정 정보")
    print("=" * 60)
    Config.print_config()
    
    print("\n🧪 설정 검증...")
    try:
        Config.validate_config()
        print("🎉 모든 설정이 올바르게 구성되었습니다!")
        print("💰 OpenAI API 비용이 발생하지 않습니다!")
    except ValueError as e:
        print(f"❌ 설정 오류: {e}")
        print("\n🔧 환경 설정을 시작하려면:")
        print("python3 config.py setup")
