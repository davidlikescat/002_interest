# interest_main.py - 은행별 분기 처리 버전

import discord
import os
import asyncio
from dotenv import load_dotenv

# interest_sub.py에서 구현된 모듈들을 임포트
from interest_sub import (
    extract_interest_amount,
    calculate_interest_distribution,
    create_text_message,
    send_telegram_message
)

# 환경 변수 로딩
load_dotenv()

# 환경 변수 로딩
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# 은행별 텔레그램 채팅 ID
TELEGRAM_BUAN_CHAT_ID = int(os.getenv('TELEGRAM_BUAN_CHAT_ID'))
TELEGRAM_GOCHANG_CHAT_ID = int(os.getenv('TELEGRAM_GOCHANG_CHAT_ID'))

# 디스코드 클라이언트 설정
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def get_telegram_chat_id(bank_branch: str) -> int:
    """은행 지점에 따라 적절한 텔레그램 채팅 ID를 반환"""
    if "부안중앙농협" in bank_branch:
        return TELEGRAM_BUAN_CHAT_ID
    elif "고창농협" in bank_branch:
        return TELEGRAM_GOCHANG_CHAT_ID
    else:
        # 기본값으로 부안중앙농협 사용
        print(f"⚠️ 알 수 없는 은행 지점: {bank_branch}, 부안중앙농협 채팅으로 전송")
        return TELEGRAM_BUAN_CHAT_ID

@client.event
async def on_ready():
    print(f'✅ Discord 봇 로그인 성공: {client.user}')
    print(f'📡 모니터링 채널 ID: {DISCORD_CHANNEL_ID}')
    print(f'📱 부안중앙농협 텔레그램 채팅 ID: {TELEGRAM_BUAN_CHAT_ID}')
    print(f'📱 고창농협 텔레그램 채팅 ID: {TELEGRAM_GOCHANG_CHAT_ID}')

@client.event
async def on_message(message):
    # 봇 자신의 메시지는 무시
    if message.author == client.user:
        return

    # 지정된 채널에서만 동작
    if message.channel.id == DISCORD_CHANNEL_ID:
        print(f"📨 메시지 감지: {message.content[:100]}...")

        try:
            # 1. 이자 금액 및 은행 지점 추출
            extraction_result = extract_interest_amount(message.content)

            if extraction_result is not None:
                interest_amount, bank_branch = extraction_result

                print(f"💰 추출된 이자 금액: {interest_amount:,}원")
                print(f"🏛️ 추출된 은행 지점: {bank_branch}")

                # 2. 은행별 텔레그램 채팅 ID 결정
                target_chat_id = get_telegram_chat_id(bank_branch)
                print(f"📱 대상 텔레그램 채팅 ID: {target_chat_id}")

                # 3. 이자 배분 계산 (은행 정보 전달)
                distribution_results = calculate_interest_distribution(interest_amount, bank_branch)
                print(f"📊 배분 결과: {distribution_results}")

                # 4. 텔레그램 메시지 생성
                telegram_text = create_text_message(
                    distribution_results, 
                    interest_amount, 
                    bank_branch, 
                    message.content  # 원본 Discord 메시지 전달
                )
                
                # 5. 은행별 텔레그램으로 전송
                try:
                    await send_telegram_message(
                        telegram_bot_token=TELEGRAM_BOT_TOKEN,
                        chat_id=target_chat_id,  # 은행별 채팅 ID 사용
                        message_text=telegram_text,
                        image_path=None
                    )
                    
                    # 성공 시 체크 반응
                    await message.add_reaction('✅')
                    print(f"✅ 텔레그램 메시지 전송 완료 ({bank_branch} → {target_chat_id})")
                    
                except Exception as telegram_error:
                    print(f"❌ 텔레그램 전송 실패: {telegram_error}")
                    # 실패 시 X 반응
                    await message.add_reaction('❌')
                
            else:
                print(f"⚠️ 이자 금액을 찾을 수 없는 메시지: {message.content[:50]}...")
                
        except Exception as e:
            print(f"❌ 메시지 처리 중 예상치 못한 오류 발생: {e}")
            await message.add_reaction('❌')

# 메인 실행부
if __name__ == '__main__':
    print("🚀 이자 배분 봇을 시작합니다... (은행별 분기 처리)")
    
    try:
        print("🔗 Discord 봇에 연결 중...")
        client.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"❌ 봇 실행 중 오류 발생: {e}")
        print("💡 Discord 토큰을 확인해주세요.")