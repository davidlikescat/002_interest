#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간소화된 알림 시스템
Telegram 봇을 통한 뉴스 수집 결과 알림
"""

import requests
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class Notifier:
    """간소화된 Telegram 알림 시스템"""

    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_success_notification(self, articles: List[Dict], notion_url: Optional[str] = None) -> bool:
        """성공 알림 전송"""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram 설정이 누락되어 알림을 보낼 수 없습니다")
            return False

        try:
            message = self._build_success_message(articles, notion_url)
            return self._send_message(message)

        except Exception as e:
            logger.error(f"성공 알림 전송 실패: {e}")
            return False

    def send_error_notification(self, error_message: str) -> bool:
        """오류 알림 전송"""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram 설정이 누락되어 알림을 보낼 수 없습니다")
            return False

        try:
            message = self._build_error_message(error_message)
            return self._send_message(message)

        except Exception as e:
            logger.error(f"오류 알림 전송 실패: {e}")
            return False

    def _build_success_message(self, articles: List[Dict], notion_url: Optional[str]) -> str:
        """성공 메시지 구성"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 기본 성공 메시지
        message = f"""🤖 <b>AI 뉴스 수집 완료</b>

📅 <b>수집 시간:</b> {current_time}
📊 <b>수집 기사:</b> {len(articles)}개

"""

        # 기사 요약 (최대 5개만 표시)
        if articles:
            message += "📰 <b>주요 뉴스:</b>\n"

            for i, article in enumerate(articles[:5], 1):
                title = article.get('title', 'No Title')
                source = article.get('source', 'Unknown')

                # 제목 길이 제한
                if len(title) > 50:
                    title = title[:50] + "..."

                message += f"{i}. <b>{title}</b>\n"
                message += f"   📰 {source}\n\n"

            # 더 많은 기사가 있다면
            if len(articles) > 5:
                message += f"⋯ 외 {len(articles) - 5}개 기사\n\n"

        # Notion 링크 (전체 기사 확인용)
        if notion_url:
            message += f"📋 <b>전체 기사 보기:</b> <a href='{notion_url}'>여기를 클릭하세요</a>\n\n"

        # 개발자 정보
        message += """━━━━━━━━━━━━━━━━━━━━
<b>개발자:</b> Joonmo Yang
<b>시스템:</b> Google News Crawler v1.5
<b>기술스택:</b> Python, Google News RSS, Notion API, Telegram Bot API, BeautifulSoup4, Feedparser, Schedule, Google Sheets API
<b>문의:</b> davidlikescat@icloud.com

© 2025 Joonmo Yang. Google News AI Automation. All rights reserved."""

        return message

    def _build_error_message(self, error_message: str) -> str:
        """오류 메시지 구성"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        message = f"""❌ <b>Google News AI 수집 실패</b>

📅 <b>발생 시간:</b> {current_time}
🚨 <b>오류 내용:</b> {error_message}

🔧 <b>확인 사항:</b>
• 인터넷 연결 상태
• Google News 접근 가능 여부
• Notion API 설정
• 환경 변수 설정

🤖 <i>Google News AI Agent v2.0</i>"""

        return message

    def _send_message(self, message: str) -> bool:
        """Telegram 메시지 전송"""
        try:
            url = f"{self.base_url}/sendMessage"

            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }

            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()

            result = response.json()

            if result.get('ok'):
                logger.info("Telegram 알림 전송 성공")
                return True
            else:
                logger.error(f"Telegram API 오류: {result.get('description', 'Unknown error')}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Telegram 전송 네트워크 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"Telegram 전송 오류: {e}")
            return False

    def test_connection(self) -> bool:
        """Telegram 봇 연결 테스트"""
        if not self.bot_token or not self.chat_id:
            print("❌ Telegram 설정이 누락되었습니다")
            return False

        try:
            # 봇 정보 조회
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            result = response.json()

            if result.get('ok'):
                bot_info = result.get('result', {})
                bot_name = bot_info.get('first_name', 'Unknown')
                print(f"✅ Telegram 봇 연결 성공: {bot_name}")

                # 테스트 메시지 전송
                test_message = "🧪 <b>Telegram 봇 연결 테스트</b>\n\nGoogle News AI Agent가 정상적으로 작동합니다!"
                if self._send_message(test_message):
                    print("✅ 테스트 메시지 전송 성공")
                    return True
                else:
                    print("❌ 테스트 메시지 전송 실패")
                    return False
            else:
                print(f"❌ Telegram 봇 정보 조회 실패: {result.get('description', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"❌ Telegram 연결 테스트 오류: {e}")
            return False

    def send_startup_notification(self) -> bool:
        """시스템 시작 알림"""
        message = f"""🚀 <b>Google News AI Agent 시작</b>

📅 <b>시작 시간:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
⚙️ <b>시스템:</b> v2.0 (Simplified)
💰 <b>특징:</b> OpenAI API 비용 없음

🤖 자동 뉴스 수집을 시작합니다..."""

        return self._send_message(message)

    def send_schedule_notification(self, next_run_time: str) -> bool:
        """스케줄 설정 알림"""
        message = f"""⏰ <b>Google News AI 스케줄러 설정</b>

📅 <b>다음 실행:</b> {next_run_time}
🔄 <b>실행 주기:</b> 매일 07:30 (한국시간)
🤖 <b>상태:</b> 대기 중

자동 뉴스 수집이 예약되었습니다."""

        return self._send_message(message)


def test_notifier():
    """알림 시스템 테스트"""
    print("🧪 Telegram 알림 시스템 테스트")
    print("=" * 50)

    notifier = Notifier()

    # 연결 테스트
    if not notifier.test_connection():
        return False

    # 테스트 데이터
    test_articles = [
        {
            'title': 'ChatGPT 신기능 출시로 AI 업계 주목',
            'source': '테크뉴스',
            'published': datetime.now(),
            'found_keywords': ['ChatGPT', 'AI', 'OpenAI']
        },
        {
            'title': '구글 바드 AI, 한국어 지원 확대',
            'source': 'AI타임즈',
            'published': datetime.now(),
            'found_keywords': ['구글', 'AI', '바드']
        }
    ]

    # 성공 알림 테스트
    print("📤 성공 알림 테스트...")
    success = notifier.send_success_notification(test_articles, "https://notion.so/test-page")

    if success:
        print("✅ 성공 알림 전송 완료")
    else:
        print("❌ 성공 알림 전송 실패")

    # 오류 알림 테스트
    print("📤 오류 알림 테스트...")
    error_success = notifier.send_error_notification("테스트 오류 메시지입니다")

    if error_success:
        print("✅ 오류 알림 전송 완료")
    else:
        print("❌ 오류 알림 전송 실패")

    return success and error_success


if __name__ == "__main__":
    test_notifier()