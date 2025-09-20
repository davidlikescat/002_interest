#!/usr/bin/env python3
"""
각 그룹에 테스트 메시지를 보내서 어떤 그룹이 어떤 은행인지 확인
"""

import asyncio
from telegram import Bot

async def test_groups():
    bot_token = "7764338164:AAHQiqgLtaebtHo1NMfHjz1nogmYIy62Zd4"
    
    groups = {
        "진동(4)": -1002449370643,
        "통정308": -1002678770086,
        "개인채팅": 7416961176
    }
    
    bot = Bot(token=bot_token)
    
    print("🧪 각 채팅에 테스트 메시지 전송 중...")
    
    for name, chat_id in groups.items():
        try:
            message = f"""🧪 이자 배분 봇 테스트

안녕하세요! 이자 배분 봇 설정을 확인하고 있습니다.

📱 채팅 정보:
• 이름: {name}
• 채팅 ID: {chat_id}

💡 이 그룹이 어떤 은행 그룹인지 확인해주세요:
• 부안중앙농협 그룹이면 → "부안" 이라고 답장
• 고창농협 그룹이면 → "고창" 이라고 답장
• 개인 채팅이면 → 답장 안 하셔도 됩니다

설정이 완료되면 실제 이자 배분 메시지를 받을 수 있습니다! ✅"""

            await bot.send_message(chat_id=chat_id, text=message)
            print(f"✅ {name} ({chat_id}) 전송 성공")
            
        except Exception as e:
            print(f"❌ {name} ({chat_id}) 전송 실패: {e}")
    
    print("\n🎯 이제 각 그룹에서 답장을 확인하고 .env 파일을 최종 업데이트하세요!")

if __name__ == "__main__":
    asyncio.run(test_groups())
