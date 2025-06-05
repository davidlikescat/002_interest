#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google News AI 간단 스케줄러
정기적으로 뉴스 수집 및 전송 (Discord 기능 제외)
"""

import schedule
import time
import subprocess
import sys
import os
import logging
from datetime import datetime, timedelta
from config import Config

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleScheduler:
    """간단한 Google News AI 스케줄러"""
    
    def __init__(self):
        self.config = Config
        # 현재 작업 디렉토리 사용
        self.script_dir = os.getcwd()
        self.main_script = 'main_004.py'  # main.py 대신 main_004.py 사용
        
        # 실행 상태 관리
        self.is_running = False
        self.execution_count = 0
        self.last_execution = None
        self.last_success = None
        
    def run_news_collection(self):
        """뉴스 수집 실행"""
        if self.is_running:
            logger.warning("⚠️ 이미 실행 중입니다. 스케줄 건너뜀")
            return False
        
        try:
            self.is_running = True
            self.execution_count += 1
            start_time = datetime.now()
            
            logger.info("🚀 Google News AI 자동 수집 시작")
            logger.info(f"📊 실행 횟수: {self.execution_count}")
            logger.info(f"⏰ 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # main_004.py 실행
            result = subprocess.run(
                [sys.executable, self.main_script],
                capture_output=True,
                text=True,
                timeout=600,  # 10분 타임아웃
                cwd=self.script_dir
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            self.last_execution = end_time
            
            if result.returncode == 0:
                # 성공
                self.last_success = end_time
                logger.info("✅ 뉴스 수집 성공")
                logger.info(f"⏱️ 소요시간: {duration:.1f}초")
                
                # 성공 결과 로그
                if result.stdout:
                    success_lines = [line for line in result.stdout.split('\n') if line.strip()]
                    if success_lines:
                        logger.info("📋 실행 결과:")
                        for line in success_lines[-5:]:  # 마지막 5줄만
                            logger.info(f"   {line}")
                
                return True
            else:
                # 실패
                logger.error("❌ 뉴스 수집 실패")
                logger.error(f"Exit code: {result.returncode}")
                logger.error(f"소요시간: {duration:.1f}초")
                
                if result.stderr:
                    logger.error(f"Error output: {result.stderr}")
                
                # 에러 알림 전송
                self._send_error_notification(result.stderr or "Unknown error")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("⏰ 실행 시간 초과 (10분)")
            self._send_error_notification("실행 시간 초과")
            return False
        except Exception as e:
            logger.error(f"❌ 예상치 못한 오류: {e}")
            self._send_error_notification(str(e))
            return False
        finally:
            self.is_running = False
    
    def _send_error_notification(self, error_message):
        """에러 발생 시 텔레그램 알림"""
        try:
            error_script = f"""
import sys
sys.path.append('{self.script_dir}')
from telegram_sender import TelegramSender
telegram = TelegramSender()
error_msg = '🚨 스케줄 실행 오류\\n\\n{error_message[:200]}\\n\\n시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
telegram.send_error_notification(error_msg)
"""
            subprocess.run([sys.executable, '-c', error_script], timeout=30)
            logger.info("📱 에러 알림 전송됨")
        except Exception as e:
            logger.error(f"에러 알림 전송 실패: {e}")
    
    def setup_schedule(self):
        """스케줄 설정"""
        # 매일 지정된 시간에 실행
        schedule.every().day.at(self.config.SCHEDULE_TIME).do(self.run_news_collection)
        
        logger.info("📅 스케줄 설정 완료:")
        logger.info(f"   • 실행 시간: 매일 {self.config.SCHEDULE_TIME}")
        logger.info(f"   • 작업: Google News AI 자동 수집")
        logger.info(f"   • 결과: Notion + Telegram 자동 전송")
        
        # 다음 실행 시간 표시
        next_run = schedule.next_run()
        if next_run:
            logger.info(f"   • 다음 실행: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def get_status(self):
        """현재 상태 반환"""
        next_run = schedule.next_run()
        
        status = {
            'is_running': self.is_running,
            'execution_count': self.execution_count,
            'last_execution': self.last_execution.strftime('%Y-%m-%d %H:%M:%S') if self.last_execution else None,
            'last_success': self.last_success.strftime('%Y-%m-%d %H:%M:%S') if self.last_success else None,
            'next_run': next_run.strftime('%Y-%m-%d %H:%M:%S') if next_run else None,
            'schedule_time': self.config.SCHEDULE_TIME
        }
        
        return status
    
    def print_status(self):
        """상태 출력"""
        status = self.get_status()
        
        print("\n📊 Google News AI 스케줄러 상태:")
        print("=" * 60)
        print(f"🔄 현재 상태: {'실행 중' if status['is_running'] else '대기 중'}")
        print(f"📅 스케줄 시간: 매일 {status['schedule_time']}")
        print(f"⏰ 다음 실행: {status['next_run'] or '설정되지 않음'}")
        print(f"📊 총 실행 횟수: {status['execution_count']}회")
        print(f"🕐 마지막 실행: {status['last_execution'] or '없음'}")
        print(f"✅ 마지막 성공: {status['last_success'] or '없음'}")
        
        # 성공률 계산
        if status['execution_count'] > 0:
            success_count = 1 if status['last_success'] else 0
            success_rate = (success_count / status['execution_count']) * 100
            print(f"📈 성공률: {success_rate:.1f}%")
    
    def test_run(self):
        """테스트 실행"""
        print("🧪 Google News AI 테스트 실행")
        print("=" * 50)
        
        success = self.run_news_collection()
        
        if success:
            print("\n✅ 테스트 성공!")
            print("📱 Notion과 Telegram을 확인해보세요")
        else:
            print("\n❌ 테스트 실패")
            print("📋 로그를 확인하여 문제를 해결하세요")
        
        return success
    
    def run_once(self):
        """한 번만 실행"""
        logger.info("⚡ 수동 실행 시작")
        return self.run_news_collection()
    
    def run_scheduler(self):
        """스케줄러 실행 (메인 루프)"""
        logger.info("🚀 Google News AI 스케줄러 시작")
        logger.info("=" * 60)
        logger.info(f"🔧 프로젝트: {self.config.PROJECT_CODE}")
        logger.info(f"⚙️ 시스템: {self.config.SYSTEM_NAME} {self.config.SYSTEM_VERSION}")
        
        # 설정 검증
        try:
            self.config.validate_config()
        except ValueError as e:
            logger.error(f"❌ 설정 오류: {e}")
            print("💡 .env 파일의 API 키 설정을 확인하세요")
            return False
        
        # 스케줄 설정
        self.setup_schedule()
        
        # 시작 알림
        try:
            start_script = f"""
import sys
sys.path.append('{self.script_dir}')
from telegram_sender import TelegramSender
telegram = TelegramSender()
msg = '🤖 Google News AI 스케줄러 시작\\n\\n⏰ 실행 시간: 매일 {self.config.SCHEDULE_TIME}\\n📅 다음 실행: {schedule.next_run().strftime("%Y-%m-%d %H:%M:%S") if schedule.next_run() else "미정"}'
telegram.send_notification(msg)
"""
            subprocess.run([sys.executable, '-c', start_script], timeout=30)
            logger.info("📱 시작 알림 전송됨")
        except Exception as e:
            logger.warning(f"시작 알림 전송 실패: {e}")
        
        # 메인 루프
        try:
            logger.info("🔄 스케줄러 메인 루프 시작")
            logger.info("   Press Ctrl+C to stop")
            
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
                
        except KeyboardInterrupt:
            logger.info("⏹️ 스케줄러 종료")
            self.print_status()
            
            # 종료 알림
            try:
                stop_script = f"""
import sys
sys.path.append('{self.script_dir}')
from telegram_sender import TelegramSender
telegram = TelegramSender()
msg = '⏹️ Google News AI 스케줄러 종료\\n\\n📊 총 실행: {self.execution_count}회\\n🕐 종료 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
telegram.send_notification(msg)
"""
                subprocess.run([sys.executable, '-c', stop_script], timeout=30)
            except Exception as e:
                logger.warning(f"종료 알림 전송 실패: {e}")
                
        except Exception as e:
            logger.error(f"❌ 스케줄러 오류: {e}")
            return False
        
        return True

def main():
    """메인 실행"""
    import sys
    
    scheduler = SimpleScheduler()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            scheduler.test_run()
        elif command == "once":
            success = scheduler.run_once()
            print(f"{'✅ 성공' if success else '❌ 실패'}")
        elif command == "status":
            scheduler.print_status()
        elif command == "config":
            Config.print_config()
        elif command == "help":
            print("Google News AI 스케줄러 사용법:")
            print("=" * 50)
            print("  python3 simple_scheduler.py        # 스케줄러 시작")
            print("  python3 simple_scheduler.py test   # 테스트 실행")
            print("  python3 simple_scheduler.py once   # 한 번만 실행")
            print("  python3 simple_scheduler.py status # 상태 확인")
            print("  python3 simple_scheduler.py config # 설정 정보")
            print("  python3 simple_scheduler.py help   # 도움말")
            print("\n💡 Tips:")
            print("  • 스케줄러는 백그라운드에서 실행됩니다")
            print("  • Ctrl+C로 종료할 수 있습니다")
            print("  • 로그는 scheduler.log에 저장됩니다")
        else:
            print(f"❌ 알 수 없는 명령어: {command}")
            print("도움말: python3 simple_scheduler.py help")
    else:
        # 기본 실행: 스케줄러 시작
        scheduler.run_scheduler()

if __name__ == "__main__":
    main()
