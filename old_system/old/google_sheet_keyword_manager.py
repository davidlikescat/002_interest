#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Sheet에서 키워드를 가져오는 모듈
"""

import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# .env 파일 로드
env_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print("⚠️ .env 파일을 찾을 수 없습니다. 환경 변수를 직접 확인합니다.")

class KeywordManager:
    """구글 시트에서 키워드를 관리하는 클래스"""
    
    def __init__(self, sheet_id=None, credentials_path=None):
        """
        KeywordManager 초기화
        
        Args:
            sheet_id (str): 구글 시트 ID
            credentials_path (str): 서비스 계정 인증 파일 경로
        """
        self.sheet_id = sheet_id or os.getenv('GOOGLE_SHEET_ID')
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH')
        self.client = None
        self.sheet = None
        
        if not self.sheet_id:
            print("⚠️ 구글 시트 ID가 설정되지 않았습니다.")
        
        if not self.credentials_path:
            print("⚠️ 구글 서비스 계정 인증 파일 경로가 설정되지 않았습니다.")
    
    def connect(self):
        """구글 시트에 연결"""
        try:
            # 구글 API 사용 권한 범위 설정
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # 서비스 계정 인증 정보 로드
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_path, scope
            )
            
            # gspread 클라이언트 생성
            self.client = gspread.authorize(credentials)
            
            # 시트 열기
            self.sheet = self.client.open_by_key(self.sheet_id)
            
            print(f"✅ 구글 시트 '{self.sheet.title}' 연결 성공")
            return True
        
        except Exception as e:
            print(f"❌ 구글 시트 연결 실패: {e}")
            return False
    
    def get_keywords(self, worksheet_name="Sheet1", keyword_column="keyword", category_column="category", active_column="active"):
        """
        지정된 워크시트에서 키워드 가져오기
        
        Args:
            worksheet_name (str): 워크시트 이름
            keyword_column (str): 키워드가 있는 열 이름
            category_column (str): 카테고리가 있는 열 이름
            active_column (str): 활성화 여부가 있는 열 이름
            
        Returns:
            tuple: (AI 키워드 리스트, 기술 키워드 리스트)
        """
        if not self.client:
            if not self.connect():
                return [], []
        
        try:
            # 워크시트 선택
            worksheet = self.sheet.worksheet(worksheet_name)
            
            # 모든 데이터 가져오기
            data = worksheet.get_all_records()
            
            if not data:
                print(f"⚠️ '{worksheet_name}' 워크시트에 데이터가 없습니다.")
                return [], []
            
            # 키워드 추출
            ai_keywords = []
            tech_keywords = []
            
            for row in data:
                # 키워드가 있고 active가 TRUE인 경우만 처리
                if (keyword_column in row and 
                    row[keyword_column] and 
                    active_column in row and 
                    str(row[active_column]).upper() == 'TRUE'):
                    
                    keyword = row[keyword_column].strip()
                    
                    # 카테고리에 따라 AI 또는 기술 키워드로 분류
                    if category_column in row:
                        category = row[category_column].strip().upper() if row[category_column] else ""
                        
                        if category == 'AI':
                            ai_keywords.append(keyword)
                        elif category in ['TECH', '기술']:
                            tech_keywords.append(keyword)
                        else:
                            # 카테고리가 지정되지 않았거나 알 수 없는 경우, AI 키워드로 처리
                            ai_keywords.append(keyword)
                    else:
                        # 카테고리 열이 없는 경우, AI 키워드로 처리
                        ai_keywords.append(keyword)
            
            print(f"✅ AI 키워드 {len(ai_keywords)}개, 기술 키워드 {len(tech_keywords)}개 로드 완료")
            return ai_keywords, tech_keywords
        
        except Exception as e:
            print(f"❌ 키워드 로드 실패: {e}")
            return [], []
    
    def get_all_keywords(self):
        """모든 키워드 가져오기 (AI + 기술)"""
        ai_keywords, tech_keywords = self.get_keywords()
        return ai_keywords + tech_keywords
    
    def print_keywords(self):
        """로드된 키워드 출력"""
        ai_keywords, tech_keywords = self.get_keywords()
        
        print("🔍 AI 키워드:")
        for i, keyword in enumerate(ai_keywords, 1):
            print(f"  {i}. {keyword}")
        
        print("\n🔧 기술 키워드:")
        for i, keyword in enumerate(tech_keywords, 1):
            print(f"  {i}. {keyword}")

# 기본 사용법 예시
if __name__ == "__main__":
    manager = KeywordManager()
    ai_keywords, tech_keywords = manager.get_keywords()
    
    print(f"🤖 AI 키워드 ({len(ai_keywords)}개):")
    for keyword in ai_keywords:
        print(f"  - {keyword}")
    
    print(f"\n💻 기술 키워드 ({len(tech_keywords)}개):")
    for keyword in tech_keywords:
        print(f"  - {keyword}")