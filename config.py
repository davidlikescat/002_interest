#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간소화된 Google News AI 시스템 설정
기사 수집 → Notion 저장 → Telegram 전송 (OpenAI 제거)
"""

import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# .env 파일 로드
env_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print("⚠️ .env 파일을 찾을 수 없습니다. 환경 변수를 직접 확인합니다.")

class Config:
    """간소화된 Google News AI 시스템 설정"""

    # 프로젝트 정보
    PROJECT_CODE = "004_google_news_ai"
    SYSTEM_NAME = "Google News AI Agent"
    SYSTEM_VERSION = "v2.0 (Simplified)"
    DEVELOPER_NAME = "양준모"
    DEVELOPER_EMAIL = "davidlikescat@icloud.com"

    # 뉴스 수집 설정
    MAX_ARTICLES = 10
    SEARCH_HOURS = 24

    # 📍 필수 API 설정 (4개만)
    NOTION_API_KEY = os.getenv('NOTION_API_KEY')
    NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    # 스케줄 설정
    SCHEDULE_TIME = "07:30"  # 한국시간 고정
    TIMEZONE = "Asia/Seoul"

    # 크롤링 설정
    REQUEST_TIMEOUT = 20
    REQUEST_DELAY = 1.0

    # 로그 설정
    LOG_LEVEL = "INFO"
    LOG_FILE = "news_agent.log"

    @classmethod
    def get_korea_time(cls):
        """현재 한국시간 반환"""
        kst = timezone(timedelta(hours=9))
        return datetime.now(kst)

    @classmethod
    def validate_config(cls):
        """필수 설정 검증 (간소화)"""
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
            raise ValueError(error_msg)

        print("✅ 필수 설정 검증 완료")
        return True

    @classmethod
    def print_config(cls):
        """설정 정보 출력 (간소화)"""
        korea_time = cls.get_korea_time()

        print(f"🔧 프로젝트: {cls.PROJECT_CODE}")
        print(f"⚙️ 시스템: {cls.SYSTEM_NAME} {cls.SYSTEM_VERSION}")
        print(f"👤 개발자: {cls.DEVELOPER_NAME}")
        print(f"🕐 현재 한국시간: {korea_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"⏰ 스케줄 시간: 매일 {cls.SCHEDULE_TIME} ({cls.TIMEZONE})")
        print(f"📊 수집 기사 수: {cls.MAX_ARTICLES}개")

        # API 설정 상태 (필수만)
        apis = {
            'Notion': bool(cls.NOTION_API_KEY and cls.NOTION_DATABASE_ID),
            'Telegram': bool(cls.TELEGRAM_BOT_TOKEN and cls.TELEGRAM_CHAT_ID)
        }

        print("🔗 API 설정 상태:")
        for api, status in apis.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {api}")

        print("💰 OpenAI API: 사용 안함 (비용 절약)")


def setup_environment():
    """환경 설정 가이드 (간소화)"""
    print("🔧 Google News AI Agent 환경 설정")
    print("=" * 50)

    # .env 파일 예제 생성
    env_example = """# Google News AI Agent 환경변수 (필수 4개만)

# Notion API 설정
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_notion_database_id_here

# Telegram Bot 설정
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
"""

    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_example)

    print("📄 .env.example 파일이 생성되었습니다")
    print("🔑 필수 API 키 4개만 설정하세요")
    print("💰 OpenAI API 불필요 - 비용 없음!")

    # 설정 상태 확인
    try:
        Config.validate_config()
    except ValueError as e:
        print(f"⚠️ {e}")
        print("💡 .env 파일을 확인하고 필요한 API 키를 설정하세요")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "setup":
            setup_environment()
        elif command == "help":
            print("사용법:")
            print("  python3 config.py       # 설정 정보 출력")
            print("  python3 config.py setup # 환경 설정 가이드")
            print("  python3 config.py help  # 도움말")
        else:
            print(f"❌ 알 수 없는 명령어: {command}")
            print("python3 config.py help 로 도움말을 확인하세요")
    else:
        print("📋 Google News AI Agent 설정 정보")
        print("=" * 50)
        Config.print_config()

        print("\n🧪 설정 검증...")
        try:
            Config.validate_config()
            print("🎉 모든 설정이 올바르게 구성되었습니다!")
        except ValueError as e:
            print(f"❌ 설정 오류: {e}")
            print("\n🔧 환경 설정을 시작하려면:")
            print("python3 config.py setup")