import asyncio
from telegram import Bot
from telegram.error import TelegramError

async def debug_telegram_bot():
    """텔레그램 봇 상태와 채팅 정보를 확인합니다"""
    bot_token = "7764338164:AAHQiqgLtaebtHo1NMfHjz1nogmYIy62Zd4"
    current_chat_id = -4980503308
    
    bot = Bot(token=bot_token)
    
    print("🤖 텔레그램 봇 디버깅 시작...")
    
    try:
        # 1. 봇 정보 확인
        bot_info = await bot.get_me()
        print(f"✅ 봇 정보:")
        print(f"   - 이름: {bot_info.first_name}")
        print(f"   - 사용자명: @{bot_info.username}")
        print(f"   - ID: {bot_info.id}")
        print()
        
        # 2. 현재 설정된 채팅 ID로 테스트
        print(f"🔍 현재 채팅 ID 테스트: {current_chat_id}")
        try:
            await bot.send_message(
                chat_id=current_chat_id, 
                text="🧪 테스트 메시지입니다. 이 메시지가 보이면 설정이 올바릅니다!"
            )
            print(f"✅ 채팅 ID {current_chat_id}로 메시지 전송 성공!")
            return
        except TelegramError as e:
            print(f"❌ 채팅 ID {current_chat_id} 전송 실패: {e}")
        
        # 3. 최근 업데이트에서 채팅 정보 찾기
        print("\n📨 최근 메시지에서 채팅 정보 찾는 중...")
        updates = await bot.get_updates(limit=100)
        
        if not updates:
            print("❌ 최근 메시지가 없습니다.")
            print("\n💡 해결 방법:")
            print("1. 텔레그램에서 봇을 찾으세요: @이자관리봇 (또는 봇 사용자명)")
            print("2. 봇과 개인 대화를 시작하고 '/start' 메시지를 보내세요")
            print("3. 또는 봇을 그룹에 추가하고 아무 메시지나 보내세요")
            print("4. 그 후 이 스크립트를 다시 실행하세요")
            return
        
        print(f"📊 {len(updates)}개의 최근 메시지를 찾았습니다:")
        print("-" * 50)
        
        seen_chats = set()
        for i, update in enumerate(updates[-10:], 1):  # 최근 10개만 표시
            if update.message:
                chat = update.message.chat
                if chat.id not in seen_chats:
                    seen_chats.add(chat.id)
                    
                    print(f"{i}. 채팅 정보:")
                    print(f"   📱 채팅 ID: {chat.id}")
                    print(f"   📝 채팅 타입: {chat.type}")
                    
                    if chat.type == 'private':
                        print(f"   👤 개인 채팅: {chat.first_name}")
                    elif chat.type in ['group', 'supergroup']:
                        print(f"   👥 그룹 채팅: {chat.title}")
                    elif chat.type == 'channel':
                        print(f"   📢 채널: {chat.title}")
                    
                    print(f"   💬 메시지: {update.message.text[:50]}...")
                    print(f"   ⏰ 시간: {update.message.date}")
                    
                    # 테스트 메시지 전송
                    try:
                        await bot.send_message(
                            chat_id=chat.id, 
                            text=f"🧪 테스트 메시지 - 채팅 ID: {chat.id}"
                        )
                        print(f"   ✅ 이 채팅으로 메시지 전송 가능!")
                        print(f"   🔧 .env 파일에 다음과 같이 설정하세요:")
                        print(f"   TELEGRAM_CHAT_ID={chat.id}")
                    except TelegramError as test_error:
                        print(f"   ❌ 이 채팅으로 메시지 전송 불가: {test_error}")
                    
                    print("-" * 30)
        
    except Exception as e:
        print(f"❌ 봇 정보 조회 실패: {e}")
        print("💡 봇 토큰이 올바른지 확인해주세요.")

if __name__ == "__main__":
    asyncio.run(debug_telegram_bot())