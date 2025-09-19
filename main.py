#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google News AI Agent v2.0 - 통합 실행기
간소화된 뉴스 수집 → Notion 저장 → Telegram 알림
"""

import sys
import time
import logging
import schedule
from datetime import datetime, timedelta
from typing import Optional

# 로컬 모듈 import
try:
    from config import Config
    from news_collector import NewsCollector
    from storage_manager import StorageManager
    from notifier import Notifier
except ImportError as e:
    print(f"❌ 모듈 import 오류: {e}")
    print("💡 필요한 모듈들이 있는지 확인하세요")
    sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NewsAgent:
    """Google News AI Agent 메인 클래스"""

    def __init__(self):
        self.config = Config
        self.collector = NewsCollector(max_articles=self.config.MAX_ARTICLES)
        self.storage = StorageManager()
        self.notifier = Notifier()

        # 실행 상태
        self.is_running = False
        self.last_execution = None
        self.execution_count = 0
        self.success_count = 0

    def run_collection(self) -> bool:
        """뉴스 수집 메인 실행"""
        if self.is_running:
            logger.warning("이미 실행 중입니다")
            return False

        try:
            self.is_running = True
            self.execution_count += 1
            start_time = time.time()

            logger.info("🤖 Google News AI Agent 시작")
            logger.info(f"🕐 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n🤖 Google News AI Agent v2.0")
            print("=" * 50)
            print(f"🔧 프로젝트: {self.config.PROJECT_CODE}")
            print(f"⚙️ 시스템: {self.config.SYSTEM_NAME} {self.config.SYSTEM_VERSION}")
            print(f"📊 목표: 최신 {self.config.MAX_ARTICLES}개 AI 뉴스 수집")
            print(f"💰 특징: OpenAI API 비용 없음!")
            print(f"🕐 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # 1단계: 설정 검증
            print(f"\n🔍 1단계: 설정 검증 중...")
            self.config.validate_config()
            print("✅ 설정 검증 완료")

            # 2단계: 뉴스 수집
            print(f"\n📰 2단계: AI 뉴스 수집 중...")
            articles = self.collector.collect_ai_news()

            if not articles:
                error_msg = "AI 관련 뉴스를 찾을 수 없습니다"
                print(f"❌ {error_msg}")
                self.notifier.send_error_notification(error_msg)
                return False

            print(f"✅ {len(articles)}개 AI 뉴스 수집 완료")

            # 3단계: Notion 저장
            print(f"\n💾 3단계: Notion 저장 중...")
            notion_url = self.storage.save_news_to_notion(articles)

            if not notion_url:
                error_msg = "Notion 저장에 실패했습니다"
                print(f"❌ {error_msg}")
                self.notifier.send_error_notification(error_msg)
                return False

            print(f"✅ Notion 저장 완료")
            logger.info(f"Notion URL: {notion_url}")

            # 4단계: Telegram 알림
            print(f"\n📱 4단계: Telegram 알림 전송 중...")
            telegram_success = self.notifier.send_success_notification(articles, notion_url)

            # 실행 완료 요약
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            self.last_execution = datetime.now()
            self.success_count += 1

            print("\n" + "=" * 50)
            print(f"🎉 Google News AI 수집 완료!")
            print(f"📊 처리 결과:")
            print(f"   • 수집된 기사: {len(articles)}개")

            # 언론사 통계
            sources = list(set(article.get('source', 'Unknown') for article in articles))
            print(f"   • 언론사: {len(sources)}곳")

            # 키워드 통계
            all_keywords = []
            for article in articles:
                all_keywords.extend(article.get('found_keywords', []))
            unique_keywords = len(set(all_keywords))
            print(f"   • 발견된 키워드: {unique_keywords}개")

            print(f"   • 소요시간: {duration}초")
            print(f"   • Notion 저장: ✅")
            print(f"   • Telegram 전송: {'✅' if telegram_success else '❌'}")
            print(f"   • 완료시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   • 💰 OpenAI API 비용: $0.00")

            # 주요 뉴스 헤드라인
            print(f"\n📰 수집된 AI 뉴스 TOP {min(5, len(articles))}:")
            for i, article in enumerate(articles[:5], 1):
                print(f"  {i}. {article['title']}")
                print(f"     📰 {article['source']} | 🕐 {article['published'].strftime('%Y-%m-%d %H:%M')}")

            # 주요 키워드
            if all_keywords:
                keyword_count = {}
                for kw in all_keywords:
                    keyword_count[kw] = keyword_count.get(kw, 0) + 1

                top_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:8]
                keyword_text = ' '.join([f'#{keyword}({count})' for keyword, count in top_keywords])
                print(f"\n🏷️ 발견된 키워드: {keyword_text}")

            # 성공 로그
            logger.info(f"Google News AI 수집 완료 - {len(articles)}개 기사, {duration}초, OpenAI 비용 없음")

            return True

        except Exception as e:
            error_msg = f"시스템 실행 중 오류 발생: {str(e)}"
            logger.error(f"❌ {error_msg}")
            print(f"❌ {error_msg}")

            # 에러 알림 전송
            self.notifier.send_error_notification(error_msg)

            return False

        finally:
            self.is_running = False

    def test_system(self) -> bool:
        """시스템 테스트"""
        print("🧪 Google News AI Agent 테스트")
        print("=" * 50)

        try:
            # 1. 설정 테스트
            print("1. 설정 검증...")
            self.config.validate_config()
            print("   ✅ 설정 검증 통과")

            # 2. Notion 연결 테스트
            print("2. Notion 연결 테스트...")
            if self.storage.test_connection():
                print("   ✅ Notion 연결 성공")
            else:
                print("   ❌ Notion 연결 실패")
                return False

            # 3. Telegram 연결 테스트
            print("3. Telegram 연결 테스트...")
            if self.notifier.test_connection():
                print("   ✅ Telegram 연결 성공")
            else:
                print("   ❌ Telegram 연결 실패")
                return False

            # 4. 뉴스 수집 테스트 (소량)
            print("4. 뉴스 수집 테스트...")
            test_collector = NewsCollector(max_articles=3)
            test_articles = test_collector.collect_ai_news()

            if test_articles:
                print(f"   ✅ 뉴스 수집 테스트 통과 ({len(test_articles)}개 기사)")
                for article in test_articles:
                    print(f"      • {article['title'][:50]}...")
            else:
                print("   ⚠️ 뉴스 수집 테스트 - 기사 없음")

            print("\n🎯 테스트 완료! (OpenAI API 비용 없음)")
            return True

        except Exception as e:
            print(f"   ❌ 테스트 실패: {e}")
            return False

    def get_status(self) -> dict:
        """현재 상태 반환"""
        return {
            'system_version': self.config.SYSTEM_VERSION,
            'is_running': self.is_running,
            'execution_count': self.execution_count,
            'success_count': self.success_count,
            'success_rate': f"{self.success_count/self.execution_count*100:.1f}%" if self.execution_count > 0 else "0%",
            'last_execution': self.last_execution.strftime('%Y-%m-%d %H:%M:%S') if self.last_execution else None,
            'max_articles': self.config.MAX_ARTICLES
        }

    def print_status(self):
        """상태 정보 출력"""
        status = self.get_status()

        print("\n📊 Google News AI Agent 상태:")
        print("=" * 50)
        print(f"⚙️ 시스템 버전: {status['system_version']}")
        print(f"🔄 현재 실행 상태: {'실행 중' if status['is_running'] else '대기 중'}")
        print(f"📈 총 실행 횟수: {status['execution_count']}회")
        print(f"✅ 성공 횟수: {status['success_count']}회")
        print(f"📊 성공률: {status['success_rate']}")

        if status['last_execution']:
            print(f"🕐 마지막 실행: {status['last_execution']}")

        print(f"📊 수집 설정: 최대 {status['max_articles']}개 기사")
        print(f"💰 OpenAI API 비용: $0.00")


def setup_scheduler(agent: NewsAgent):
    """스케줄러 설정"""
    schedule.clear()

    # 한국시간 07:30 = UTC 22:30 (전날)
    schedule.every().day.at("22:30").do(agent.run_collection)  # UTC 기준

    print(f"⏰ 스케줄러 설정 완료:")
    print(f"   • 실행 시간: 매일 {Config.SCHEDULE_TIME} (한국시간)")

    next_run = schedule.next_run()
    if next_run:
        # UTC를 한국시간으로 변환하여 표시
        kst_next_run = next_run + timedelta(hours=9)
        print(f"   • 다음 실행: {kst_next_run.strftime('%Y-%m-%d %H:%M:%S')} (한국시간)")


def run_scheduler(agent: NewsAgent):
    """스케줄러 실행"""
    setup_scheduler(agent)

    print(f"\n🚀 Google News AI Agent 스케줄러 시작")
    print("=" * 50)
    agent.print_status()

    print(f"\n📅 실행 방법:")
    print("⚡ 수동 실행: python3 main.py")
    print("📊 상태 확인: python3 main.py status")
    print("🧪 테스트 실행: python3 main.py test")
    print("⏹️ 종료: Ctrl+C")

    try:
        print(f"\n⏳ 스케줄 대기 중... (Ctrl+C로 종료)")

        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크

    except KeyboardInterrupt:
        print(f"\n⏹️ 스케줄러 종료")
        agent.print_status()


def print_help():
    """도움말 출력"""
    print("Google News AI Agent v2.0 (Simplified)")
    print("=" * 50)
    print("사용법:")
    print("  python3 main.py           # 메인 실행")
    print("  python3 main.py test      # 시스템 테스트")
    print("  python3 main.py status    # 상태 정보")
    print("  python3 main.py schedule  # 스케줄러 시작")
    print("  python3 main.py config    # 설정 정보")
    print("  python3 main.py help      # 도움말")
    print("\n💰 특징:")
    print("  • OpenAI API 비용 없음!")
    print("  • 간소화된 구조로 빠른 실행")
    print("  • Google News에서 AI 관련 최신 뉴스 수집")
    print("  • 기사 원문 직접 크롤링")
    print("  • Notion 데이터베이스에 자동 저장")
    print("  • Telegram으로 결과 알림 전송")
    print("\n🔗 필요한 API (4개만):")
    print("  • Notion API (무료)")
    print("  • Telegram Bot API (무료)")


def main():
    """메인 실행 함수"""
    agent = NewsAgent()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "test":
            agent.test_system()

        elif command == "status":
            agent.print_status()

        elif command == "schedule":
            run_scheduler(agent)

        elif command == "config":
            Config.print_config()

        elif command == "help":
            print_help()

        else:
            print(f"❌ 알 수 없는 명령어: {command}")
            print("도움말: python3 main.py help")
    else:
        # 메인 실행
        success = agent.run_collection()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()