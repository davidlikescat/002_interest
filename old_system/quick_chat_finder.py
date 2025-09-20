#!/usr/bin/env python3
"""
빠른 텔레그램 채팅 ID 찾기
"""

import asyncio
from telegram import Bot

async def find_chat_ids():
    bot_token = "7764338164:AAHQiqgLtaebtHo1NMfHjz1nogmYIy62Zd4"
    
    try:
        bot = Bot(token=bot_token)
        print("🤖 봇 연결 성공!")
        
        # 최근 업데이트 가져오기
        updates = await bot.get_updates(limit=50)
        
        if not updates:
            print("\n❌ 최근 메시지가 없습니다.")
            print("💡 다음과 같이 하세요:")
            print("1. 텔레그램에서 봇을 찾으세요: @이자관리봇")
            print("2. 봇과 개인 대화를 시작하고 '/start' 메시지 보내기")
            print("3. 또는 봇을 그룹에 추가하고 아무 메시지나 보내기")
            print("4. 그 후 이 스크립트를 다시 실행하세요")
            return
        
        print(f"\n📨 {len(updates)}개의 메시지를 찾았습니다:")
        print("=" * 60)
        
        seen_chats = {}
        for update in updates:
            if update.message:
                chat = update.message.chat
                
                if chat.id not in seen_chats:
                    seen_chats[chat.id] = {
                        'type': chat.type,
                        'title': chat.title or f"{chat.first_name} {chat.last_name or ''}".strip(),
                        'username': chat.username
                    }
        
        # 결과 출력
        for chat_id, info in seen_chats.items():
            print(f"\n📱 채팅 ID: {chat_id}")
            print(f"   타입: {info['type']}")
            print(f"   이름: {info['title']}")
            if info['username']:
                print(f"   사용자명: @{info['username']}")
            
            # .env 파일용 설정 제안
            if info['type'] == 'private':
                print(f"   💡 개인 채팅용: TELEGRAM_CHAT_ID={chat_id}")
            elif '부안' in info['title'] or 'buan' in info['title'].lower():
                print(f"   💡 부안용: TELEGRAM_BUAN_CHAT_ID={chat_id}")
            elif '고창' in info['title'] or 'gochang' in info['title'].lower():
                print(f"   💡 고창용: TELEGRAM_GOCHANG_CHAT_ID={chat_id}")
            else:
                print(f"   💡 일반 그룹용: TELEGRAM_GROUP_CHAT_ID={chat_id}")
            
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(find_chat_ids())
