#!/usr/bin/env python3
"""
텔레그램 이자 배분 봇 완전 테스트 스크립트
모든 기능을 단계별로 테스트합니다.
"""

import asyncio
import os
import json
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

# 환경변수 로드
load_dotenv()

# interest_sub.py에서 함수 임포트
try:
    from interest_sub import (
        extract_interest_amount,
        calculate_interest_distribution,
        create_text_message,
        send_telegram_message
    )
    print("✅ interest_sub.py 모듈 임포트 성공")
except ImportError as e:
    print(f"❌ interest_sub.py 임포트 실패: {e}")
    exit(1)

class TelegramInterestBotTester:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.buan_chat_id = os.getenv('TELEGRAM_BUAN_CHAT_ID')
        self.gochang_chat_id = os.getenv('TELEGRAM_GOCHANG_CHAT_ID')
        
        # 환경변수 검증
        self.validate_environment()
    
    def validate_environment(self):
        """환경변수 검증"""
        print("🔍 환경변수 검증 중...")
        
        missing_vars = []
        if not self.bot_token:
            missing_vars.append('TELEGRAM_BOT_TOKEN')
        if not self.buan_chat_id:
            missing_vars.append('TELEGRAM_BUAN_CHAT_ID')
        if not self.gochang_chat_id:
            missing_vars.append('TELEGRAM_GOCHANG_CHAT_ID')
        
        if missing_vars:
            print(f"❌ 누락된 환경변수: {', '.join(missing_vars)}")
            print("💡 .env 파일을 확인해주세요:")
            print("   TELEGRAM_BOT_TOKEN=your_bot_token")
            print("   TELEGRAM_BUAN_CHAT_ID=your_buan_chat_id")
            print("   TELEGRAM_GOCHANG_CHAT_ID=your_gochang_chat_id")
            exit(1)
        
        print("✅ 모든 환경변수 설정됨")
        print(f"   봇 토큰: {self.bot_token[:20]}...")
        print(f"   부안중앙농협 채팅 ID: {self.buan_chat_id}")
        print(f"   고창농협 채팅 ID: {self.gochang_chat_id}")
    
    async def test_bot_connection(self):
        """봇 연결 테스트"""
        print("\n🤖 텔레그램 봇 연결 테스트...")
        
        try:
            bot = Bot(token=self.bot_token)
            bot_info = await bot.get_me()
            
            print(f"✅ 봇 연결 성공!")
            print(f"   이름: {bot_info.first_name}")
            print(f"   사용자명: @{bot_info.username}")
            print(f"   ID: {bot_info.id}")
            return True
            
        except TelegramError as e:
            print(f"❌ 봇 연결 실패: {e}")
            return False
    
    async def test_chat_access(self):
        """채팅 접근 테스트"""
        print("\n📱 채팅 접근 테스트...")
        
        bot = Bot(token=self.bot_token)
        test_results = {}
        
        chats = {
            "부안중앙농협": self.buan_chat_id,
            "고창농협": self.gochang_chat_id
        }
        
        for name, chat_id in chats.items():
            try:
                await bot.send_message(
                    chat_id=int(chat_id),
                    text=f"🧪 {name} 채팅 테스트\n이 메시지가 보이면 설정이 올바릅니다!"
                )
                print(f"✅ {name} 채팅 접근 성공 (ID: {chat_id})")
                test_results[name] = True
                
            except TelegramError as e:
                print(f"❌ {name} 채팅 접근 실패 (ID: {chat_id}): {e}")
                test_results[name] = False
        
        return test_results
    
    def test_interest_extraction(self):
        """이자 추출 테스트"""
        print("\n💰 이자 추출 기능 테스트...")
        
        test_messages = [
            "🏦 농협대출[납입도래](061-2210-35**-**) 12월28일(이자:120,500원예상)\n▶관리점 : 부안중앙농협",
            "🏦 농협대출[납입도래](061-2210-35**-**) 01월15일(이자:95,800원예상)\n▶관리점 : 고창농협",
            "납입예상금액 : 156,700원\n관리점 : 행안농협"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n테스트 {i}: {message[:50]}...")
            result = extract_interest_amount(message)
            
            if result:
                amount, bank = result
                print(f"✅ 추출 성공: {amount:,}원, {bank}")
            else:
                print("❌ 추출 실패")
    
    def test_distribution_calculation(self):
        """배분 계산 테스트"""
        print("\n📊 배분 계산 테스트...")
        
        test_cases = [
            (100000, "부안중앙농협"),  # 3명 투자자
            (150000, "고창농협"),      # 4명 투자자
        ]
        
        for amount, bank in test_cases:
            print(f"\n{bank} - {amount:,}원 배분:")
            distribution = calculate_interest_distribution(amount, bank)
            
            for name, dist_amount in distribution.items():
                print(f"  {name}: {dist_amount:,}원")
    
    async def test_message_creation(self):
        """메시지 생성 테스트"""
        print("\n📝 메시지 생성 테스트...")
        
        # 테스트 데이터
        test_amount = 120500
        test_bank = "부안중앙농협"
        test_original = "🏦 농협대출[납입도래](061-2210-35**-**) 12월28일(이자:120,500원예상)\n▶관리점 : 부안중앙농협"
        
        # 배분 계산
        distribution = calculate_interest_distribution(test_amount, test_bank)
        
        # 메시지 생성
        message_text = create_text_message(
            distribution, test_amount, test_bank, test_original
        )
        
        print("생성된 메시지:")
        print("=" * 50)
        print(message_text)
        print("=" * 50)
        
        return message_text, test_bank
    
    async def test_full_workflow(self):
        """전체 워크플로우 테스트"""
        print("\n🚀 전체 워크플로우 테스트...")
        
        # 실제 메시지 시뮬레이션
        test_messages = [
            {
                "content": "🏦 농협대출[납입도래](061-2210-35**-**) 12월28일(이자:120,500원예상)\n▶관리점 : 부안중앙농협",
                "expected_bank": "부안중앙농협"
            },
            {
                "content": "🏦 농협대출[납입도래](061-2210-35**-**) 01월15일(이자:95,800원예상)\n▶관리점 : 고창농협", 
                "expected_bank": "고창농협"
            }
        ]
        
        for i, test_case in enumerate(test_messages, 1):
            print(f"\n--- 워크플로우 테스트 {i} ---")
            message_content = test_case["content"]
            expected_bank = test_case["expected_bank"]
            
            # 1. 이자 추출
            extraction_result = extract_interest_amount(message_content)
            if not extraction_result:
                print("❌ 이자 추출 실패")
                continue
            
            amount, bank = extraction_result
            print(f"✅ 이자 추출: {amount:,}원, {bank}")
            
            # 2. 배분 계산
            distribution = calculate_interest_distribution(amount, bank)
            print(f"✅ 배분 계산 완료")
            
            # 3. 메시지 생성
            telegram_text = create_text_message(distribution, amount, bank, message_content)
            print(f"✅ 메시지 생성 완료")
            
            # 4. 채팅 ID 결정
            if "부안중앙농협" in bank:
                target_chat_id = int(self.buan_chat_id)
            elif "고창농협" in bank:
                target_chat_id = int(self.gochang_chat_id)
            else:
                target_chat_id = int(self.buan_chat_id)  # 기본값
            
            print(f"✅ 대상 채팅 결정: {bank} → {target_chat_id}")
            
            # 5. 텔레그램 전송
            try:
                await send_telegram_message(
                    telegram_bot_token=self.bot_token,
                    chat_id=target_chat_id,
                    message_text=telegram_text
                )
                print(f"✅ 텔레그램 전송 성공!")
                
            except Exception as e:
                print(f"❌ 텔레그램 전송 실패: {e}")
    
    def check_investors_config(self):
        """investors.json 설정 확인"""
        print("\n📋 투자자 설정 확인...")
        
        if not os.path.exists('investors.json'):
            print("❌ investors.json 파일이 없습니다.")
            return False
        
        try:
            with open('investors.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print("✅ investors.json 로드 성공")
            
            for bank, investors in config.items():
                print(f"\n{bank}:")
                total_percentage = 0
                for investor in investors:
                    name = investor['name']
                    percentage = investor['percentage']
                    total_percentage += percentage
                    print(f"  {name}: {percentage*100:.1f}%")
                
                print(f"  총 비율: {total_percentage*100:.1f}%")
                
                if abs(total_percentage - 1.0) > 0.001:
                    print(f"  ⚠️ 비율 합계가 100%가 아닙니다!")
            
            return True
            
        except Exception as e:
            print(f"❌ investors.json 로드 실패: {e}")
            return False

async def main():
    """메인 테스트 함수"""
    print("🚀 텔레그램 이자 배분 봇 완전 테스트 시작")
    print("=" * 60)
    
    # 테스터 인스턴스 생성
    tester = TelegramInterestBotTester()
    
    # 1. 투자자 설정 확인
    if not tester.check_investors_config():
        print("💡 investors.json 파일을 확인해주세요.")
        return
    
    # 2. 봇 연결 테스트
    if not await tester.test_bot_connection():
        print("💡 TELEGRAM_BOT_TOKEN을 확인해주세요.")
        return
    
    # 3. 채팅 접근 테스트
    chat_results = await tester.test_chat_access()
    failed_chats = [name for name, success in chat_results.items() if not success]
    
    if failed_chats:
        print(f"\n⚠️ 접근 실패한 채팅: {', '.join(failed_chats)}")
        print("💡 봇을 해당 그룹에 추가하고 관리자 권한을 부여해주세요.")
        
        # 그래도 계속 진행할지 묻기
        response = input("\n계속 테스트를 진행하시겠습니까? (y/N): ")
        if response.lower() != 'y':
            return
    
    # 4. 기능별 테스트
    tester.test_interest_extraction()
    tester.test_distribution_calculation()
    
    # 5. 메시지 생성 테스트
    await tester.test_message_creation()
    
    # 6. 전체 워크플로우 테스트
    print("\n" + "=" * 60)
    response = input("전체 워크플로우 테스트를 실행하시겠습니까? (실제 메시지 전송) (y/N): ")
    
    if response.lower() == 'y':
        await tester.test_full_workflow()
    
    print("\n" + "=" * 60)
    print("🎉 테스트 완료!")
    print("💡 이제 Discord 봇을 실행해서 실제 메시지를 테스트해보세요:")
    print("   python interest_main.py")

if __name__ == "__main__":
    asyncio.run(main())
