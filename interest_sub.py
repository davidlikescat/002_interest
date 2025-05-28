# interest_sub.py - 올바른 계좌번호 및 투자자명 수정 버전

import re
import os
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from telegram import Bot
from telegram.error import TelegramError
import asyncio

async def send_telegram_message(telegram_bot_token: str, chat_id: int, message_text: str, image_path: str = None):
    """
    텔레그램 메시지를 전송합니다. (텍스트만)
    """
    try:
        bot = Bot(token=telegram_bot_token)
        
        # 봇 정보 확인 (디버깅용)
        bot_info = await bot.get_me()
        print(f"봇 정보: {bot_info.username} ({bot_info.id})")
        
        # 텍스트 메시지 전송
        await bot.send_message(chat_id=chat_id, text=message_text, parse_mode='HTML')
        print(f"✅ 텔레그램 텍스트 메시지 전송 완료 (채팅 ID: {chat_id})")

        # 이미지 전송 부분 제거 (텍스트만)
        print("📝 텍스트 메시지만 전송 (이미지 없음)")

    except TelegramError as e:
        print(f"❌ 텔레그램 메시지 전송 중 오류 발생: {e}")
        if "chat not found" in str(e).lower():
            print("💡 해결 방법:")
            print("   1. 텔레그램 봇을 대상 그룹/채널에 추가해주세요")
            print("   2. 올바른 채팅 ID를 확인해주세요")
            print("   3. 봇에게 메시지 보내기 권한이 있는지 확인해주세요")
        raise e
    except Exception as e:
        print(f"❌ 알 수 없는 오류로 텔레그램 메시지 전송 실패: {e}")
        raise e

def load_investors_config(config_path: str = "investors.json") -> dict:
    """
    investors.json 파일에서 은행별 투자자 정보를 로드합니다.
    """
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                investors_data = json.load(f)
            
            print(f"✅ 투자자 설정 파일 로드 완료: {config_path}")
            return investors_data
        else:
            print(f"⚠️ 투자자 설정 파일을 찾을 수 없습니다: {config_path}")
            return None
    except Exception as e:
        print(f"❌ 투자자 설정 파일 로드 중 오류: {e}")
        return None

def extract_interest_amount(message_content: str) -> tuple[int, str] | None:
    """
    메시지 내용에서 이자 금액과 농협 지점 이름을 추출합니다.
    """
    interest_amount = None
    bank_branch = None

    # 1. 이자 금액 추출 패턴
    pattern_amount1 = r"이자\s*:\s*([\d,]+)\s*원\s*예상"
    match_amount1 = re.search(pattern_amount1, message_content)

    if match_amount1:
        amount_str = match_amount1.group(1).replace(',', '')
        try:
            interest_amount = int(amount_str)
        except ValueError:
            print(f"❌ 금액 변환 실패 (패턴1): {amount_str}")
            return None

    # 2. 대체 패턴
    if interest_amount is None:
        pattern_amount2 = r"납입예상금액\s*:\s*([\d,]+)\s*원"
        match_amount2 = re.search(pattern_amount2, message_content)
        if match_amount2:
            amount_str = match_amount2.group(1).replace(',', '')
            try:
                interest_amount = int(amount_str)
            except ValueError:
                print(f"❌ 금액 변환 실패 (패턴2): {amount_str}")
                return None
    
    if interest_amount is None:
        return None

    # 3. 은행 지점 이름 추출
    if "고창농협" in message_content:
        bank_branch = "고창농협"
    elif "행안농협" in message_content:
        bank_branch = "행안농협"
    elif "부안중앙농협" in message_content:
        bank_branch = "부안중앙농협"
    elif "농협" in message_content:
        bank_branch = "농협"
    else:
        bank_branch = "알 수 없음"

    return interest_amount, bank_branch

def calculate_interest_distribution(interest_amount: int, bank_branch: str) -> dict:
    """
    은행 지점 정보에 따라 이자 금액을 배분합니다.
    은행별로 다른 투자자 구성을 사용합니다.
    """
    # investors.json에서 은행별 설정을 로드
    investors_config = load_investors_config()
    
    if investors_config and bank_branch in investors_config:
        print(f"📊 {bank_branch} 투자자 설정 사용: {investors_config[bank_branch]}")
        distribution = {}
        
        # 수수료 5% 고정
        fee_amount = int(interest_amount * 0.05)
        distribution["수수료"] = fee_amount
        
        # 나머지 95%를 투자자들에게 배분
        remaining_amount = interest_amount - fee_amount
        
        for investor in investors_config[bank_branch]:
            name = investor['name']
            ratio = investor['percentage']
            amount = int(remaining_amount * ratio)
            distribution[name] = amount
        
        return distribution
    
    # JSON 파일이 없거나 은행 정보가 없으면 기본 3명 로직 사용
    print(f"⚠️ {bank_branch}에 대한 설정을 찾을 수 없음. 기본 3명 설정 사용")
    distribution = {}
    
    # 수수료 5% 고정
    fee_amount = int(interest_amount * 0.05)
    distribution["수수료"] = fee_amount
    
    # 나머지 95%를 3등분 (투자자B는 0.01% 더 많이)
    remaining_amount = interest_amount - fee_amount
    
    distribution["투자자A"] = int(remaining_amount * 0.3333)
    distribution["투자자B"] = int(remaining_amount * 0.3334)  # 반올림 차이 흡수
    distribution["투자자C"] = int(remaining_amount * 0.3333)
    
    return distribution

def create_text_message(distribution_results: dict, total_amount: int, bank_branch: str, original_message: str = "") -> str:
    """
    요구사항에 맞는 텔레그램 메시지를 생성합니다. (수수료 제외, 계좌 정보 포함)
    은행별로 다른 투자자 구성을 지원합니다.
    """
    import re
    
    # 원본 메시지에서 정보 추출
    date_match = re.search(r'(\d{2})월(\d{2})일', original_message)
    account_match = re.search(r'(\d{3}-\d{4}-\d{2}\*\*-\*\*)', original_message)
    
    month = date_match.group(1) if date_match else datetime.now().strftime('%m')
    day = date_match.group(2) if date_match else datetime.now().strftime('%d')
    account = account_match.group(1) if account_match else "061-2210-35**-**"
    
    message = f"<b>{bank_branch} 이자 추가납입 요청 드립니다.</b>\n\n"
    message += f"🏦 농협대출[납입도래]({account}) {month}월{day}일(이자:{total_amount:,}원예상)\n"
    message += f"▶관리점 : {bank_branch}\n\n"
    
    # 🔧 업데이트된 투자자 매핑 (투자자D: 박** → 전**)
    investor_mapping = {
        "투자자A": "이**",
        "투자자B": "양**", 
        "투자자C": "김**",
        "투자자D": "전**"  # 🔧 박** → 전**로 변경
    }
    
    # 자동이체 고정금액
    AUTO_TRANSFER_AMOUNT = 36833
    
    # 수수료를 제외한 투자자들만 처리
    investors_only = {k: v for k, v in distribution_results.items() 
                     if "수수료" not in k and "잔여금" not in k}
    
    for name, interest_amount in investors_only.items():
        display_name = investor_mapping.get(name, name)
        
        if name == "투자자A":
            # 투자자A: 자동이체 36,833원 차감 후 나머지 청구
            paid_amount = AUTO_TRANSFER_AMOUNT
            additional_needed = max(0, interest_amount - AUTO_TRANSFER_AMOUNT)
            
            message += f"✅ <b>{display_name}</b>\n"
            message += f"• 이자 : {interest_amount:,}원\n"
            message += f"• 납입 : {paid_amount:,}원 (자동이체)\n"
            message += f"• 추가납입요청 : {additional_needed:,}원\n\n"
            
        elif name == "투자자B":
            # 투자자B: 항상 완납, 추가납입 0원
            message += f"✅ <b>{display_name}</b>\n"
            message += f"• 이자 : {interest_amount:,}원\n"
            message += f"• 납입 : {interest_amount:,}원 (완납)\n"
            message += f"• 추가납입요청 : 0원\n\n"
            
        else:
            # 나머지 투자자들: 미납으로 처리
            message += f"✅ <b>{display_name}</b>\n"
            message += f"• 이자 : {interest_amount:,}원\n"
            message += f"• 납입 : 0원 (미납)\n"
            message += f"• 추가납입요청 : {interest_amount:,}원\n\n"
    
    # 총 이자 표시
    message += f"📊 <i>총 이자: {total_amount:,}원</i>\n\n"
    
    # 🔧 올바른 계좌번호로 수정 (3333159564139 - 3이 4개)
    message += f"💡 <b>아래 계좌로 입금해주세요.</b>\n"
    message += f"💡 <b>3333159564139 카카오뱅크 양**</b>"
    
    return message

def create_image_message(distribution_results: dict, total_amount: int, bank_branch: str) -> str:
    """
    이자 배분 결과를 시각화한 이미지를 생성하고 파일 경로를 반환합니다.
    (현재는 사용하지 않지만 호환성을 위해 유지)
    """
    print("⚠️ 이미지 생성 함수 호출됨 (현재 사용 안 함)")
    return None
