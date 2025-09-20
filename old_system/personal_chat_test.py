import asyncio
from telegram import Bot

async def find_personal_chat():
    """개인 채팅 ID를 찾아서 테스트합니다"""
    bot_token = "7764338164:AAHQiqgLtaebtHo1NMfHjz1nogmYIy62Zd4"
    
    bot = Bot(token=bot_token)
    
    print("🔍 개인 채팅 ID 찾는 중...")
    
    try:
        updates = await bot.get_updates(limit=100)
        
        personal_chats = []
        for update in updates:
            if update.message and update.message.chat.type == 'private':
                chat = update.message.chat
                personal_chats.append({
                    'id': chat.id,
                    'name': f"{chat.first_name} {chat.last_name or ''}".strip(),
                    'username': chat.username
                })
        
        if not personal_chats:
            print("❌ 개인 채팅을 찾을 수 없습니다.")
            print("💡 텔레그램에서 @interest4408bot과 개인 대화를 시작하고")
            print("   '/start' 메시지를 보낸 후 다시 실행해주세요.")
            return
        
        print(f"✅ {len(personal_chats)}개의 개인 채팅을 찾았습니다:")
        
        for i, chat in enumerate(personal_chats, 1):
            print(f"\n{i}. 개인 채팅:")
            print(f"   📱 채팅 ID: {chat['id']}")
            print(f"   👤 이름: {chat['name']}")
            print(f"   📝 사용자명: @{chat['username'] or 'N/A'}")
            
            # 테스트 메시지 전송
            try:
                await bot.send_message(
                    chat_id=chat['id'],
                    text="🧪 개인 채팅 테스트 메시지입니다!\n이 메시지가 보이면 설정이 올바릅니다! ✅"
                )
                print(f"   ✅ 메시지 전송 성공!")
                print(f"   🔧 개인 채팅 테스트용 .env 설정:")
                print(f"   TELEGRAM_CHAT_ID={chat['id']}")
                
                # 첫 번째 성공한 개인 채팅만 사용
                return chat['id']
                
            except Exception as e:
                print(f"   ❌ 메시지 전송 실패: {e}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(find_personal_chat())