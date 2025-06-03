def create_text_message(distribution_results: dict, total_amount: int, bank_branch: str, original_message: str = "") -> str:
    """
    요구사항에 맞는 텔레그램 메시지를 생성합니다.
    🔧 수정: 은행별 자동이체 금액 처리
    """
    import re
    
    print(f"📝 텔레그램 메시지 생성: {total_amount:,}원 ({bank_branch})")
    
    # 원본 메시지에서 정보 추출
    date_match = re.search(r'(\d{2})월(\d{2})일', original_message)
    account_match = re.search(r'(\d{3}-\d{4}-\d{2}\*\*-\*\*)', original_message)
    
    month = date_match.group(1) if date_match else datetime.now().strftime('%m')
    day = date_match.group(2) if date_match else datetime.now().strftime('%d')
    account = account_match.group(1) if account_match else "061-2210-35**-**"
    
    print(f"  📅 추출된 날짜: {month}월{day}일")
    print(f"  🏦 추출된 계좌: {account}")
    
    message = f"<b>{bank_branch} 이자 추가납입 요청 드립니다.</b>\n\n"
    message += f"🏦 농협대출[납입도래]({account}) {month}월{day}일(이자:{total_amount:,}원예상)\n"
    message += f"▶관리점 : {bank_branch}\n\n"
    
    # 🔧 업데이트된 투자자 매핑
    investor_mapping = {
        "투자자A": "이**",
        "투자자B": "양**", 
        "투자자C": "김**",
        "투자자D": "전**"
    }
    
    # 🔧 은행별 자동이체 금액 설정
    if "고창농협" in bank_branch:
        AUTO_TRANSFER_AMOUNT = 168417
        print(f"  💰 고창농협 자동이체 금액: {AUTO_TRANSFER_AMOUNT:,}원")
    else:  # 부안중앙농협 등
        AUTO_TRANSFER_AMOUNT = 36833
        print(f"  💰 부안중앙농협 자동이체 금액: {AUTO_TRANSFER_AMOUNT:,}원")
    
    # 투자자별 처리
    for name, interest_amount in distribution_results.items():
        display_name = investor_mapping.get(name, name)
        
        print(f"  👤 {display_name} 처리: {interest_amount:,}원")
        
        if name == "투자자A":
            # 투자자A: 자동이체 금액 차감 후 나머지 청구
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
    
    # 🔧 올바른 계좌번호로 수정
    message += f"💡 <b>아래 계좌로 입금해주세요.</b>\n"
    message += f"💡 <b>3333159564139 카카오뱅크 양**</b>"
    
    print("✅ 텔레그램 메시지 생성 완료")
    return message
