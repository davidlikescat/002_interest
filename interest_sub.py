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
    
    # 🔧 수정된 부분: 고창농협 기본값도 4명으로 처리
    print(f"⚠️ {bank_branch}에 대한 설정을 찾을 수 없음. 기본 설정 사용")
    distribution = {}
    
    # 수수료 5% 고정
    fee_amount = int(interest_amount * 0.05)
    distribution["수수료"] = fee_amount
    
    # 나머지 95%를 배분
    remaining_amount = interest_amount - fee_amount
    
    # 🔧 고창농협인 경우 4명 지분 배분, 그 외는 3명 균등 배분
    if "고창농협" in bank_branch:
        # 고창농협 4명 지분 배분 (investors.json 데이터와 동일)
        distribution["투자자A"] = int(remaining_amount * 0.4255)  # 42.55%
        distribution["투자자B"] = int(remaining_amount * 0.2553)  # 25.53%
        distribution["투자자C"] = int(remaining_amount * 0.1596)  # 15.96%
        distribution["투자자D"] = int(remaining_amount * 0.1596)  # 15.96%
    else:
        # 부안중앙농협 등 기타: 3명 균등 배분
        distribution["투자자A"] = int(remaining_amount * 0.3333)
        distribution["투자자B"] = int(remaining_amount * 0.3334)  # 반올림 차이 흡수
        distribution["투자자C"] = int(remaining_amount * 0.3333)
    
    return distribution
