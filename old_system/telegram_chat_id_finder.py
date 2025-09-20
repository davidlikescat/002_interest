import asyncio
from telegram import Bot

async def get_chat_id():
    """텔레그램 봇의 채팅 ID를 확인하는 스크립트"""
    bot_token = "7764338164:AAHQiqgLtaebtHo1NMfHjz1nogmYIy62Zd4"  # .env에서 가져온 토큰
    
    bot = Bot(token=bot_token)
    
    try:
        # 봇의 업데이트 가져오기
        updates = await bot.get_updates()
        
        print("=== 최근 메시지/채팅 정보 ===")
        for update in updates:
            if update.message:
                chat = update.message.chat
                print(f"채팅 ID: {chat.id}")
                print(f"채팅 타입: {chat.type}")
                print(f"채팅 제목: {chat.title if chat.title else chat.first_name}")
                print(f"메시지: {update.message.text}")
                print("-" * 30)
        
        if not updates:
            print("최근 메시지가 없습니다.")
            print("봇을 그룹에 추가하고 아무 메시지나 보낸 후 다시 실행해주세요.")
            
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(get_chat_id())