#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Gemini를 이용한 기사 요약 모듈
"""

import os
import time
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# .env 파일 로드
env_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print("⚠️ .env 파일을 찾을 수 없습니다. 환경 변수를 직접 확인합니다.")

# 로깅 설정
logger = logging.getLogger(__name__)

class GeminiSummarizer:
    """Google Gemini를 이용한 기사 요약 클래스"""
    
    def __init__(self, api_key=None):
        """
        GeminiSummarizer 초기화
        
        Args:
            api_key (str): Google Gemini API 키 (없으면 환경 변수에서 가져옴)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL_NAME', 'gemini-1.5-pro')
        self.initialized = False
        
        if not self.api_key:
            print("⚠️ Gemini API 키가 설정되지 않았습니다.")
            return
            
        try:
            # Gemini API 초기화
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.initialized = True
            print(f"✅ Gemini API 초기화 완료 (모델: {self.model_name})")
        except Exception as e:
            print(f"❌ Gemini API 초기화 실패: {e}")
            logger.error(f"Gemini API 초기화 실패: {e}")
    
    def summarize_article(self, title, content, max_sentences=3, max_retries=3, retry_delay=2):
        """
        기사 내용을 Gemini를 이용해 요약
        
        Args:
            title (str): 기사 제목
            content (str): 기사 내용
            max_sentences (int): 최대 요약 문장 수
            max_retries (int): 최대 재시도 횟수
            retry_delay (int): 재시도 사이의 지연 시간(초)
            
        Returns:
            str: 요약된 내용 (실패 시 None)
        """
        if not self.initialized:
            logger.warning("Gemini API가 초기화되지 않았습니다.")
            return None
            
        # 요약 프롬프트 생성
        prompt = f"""
제목: {title}

내용: 
{content[:8000]}  # 내용이 너무 길면 앞부분 8000자만 사용

위 기사를 3문장 이내로 간결하게 요약해주세요. 
중요한 사실만 포함하고, 불필요한 세부 사항은 제외해주세요.
각 문장은 명확하고 완결된 형태로 작성해주세요.
마지막 문장은 자연스럽게 마무리되도록 작성해주세요.
한국어로 요약해주세요.
"""
        
        # 재시도 로직
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                
                if hasattr(response, 'text') and response.text:
                    summary = response.text.strip()
                    
                    # 불필요한 따옴표나 마크다운 제거
                    summary = summary.replace('```', '').strip()
                    if summary.startswith('"') and summary.endswith('"'):
                        summary = summary[1:-1].strip()
                        
                    logger.info(f"기사 요약 성공: {len(summary)} 글자")
                    return summary
                else:
                    logger.warning(f"Gemini 응답에 텍스트가 없습니다: {response}")
                    
            except Exception as e:
                logger.error(f"Gemini API 호출 중 오류 ({attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"{retry_delay}초 후 재시도...")
                    time.sleep(retry_delay)
                    
        logger.error(f"기사 요약 실패: 최대 재시도 횟수 초과")
        return None
    
    def batch_summarize(self, articles, max_articles=10):
        """
        여러 기사를 일괄 요약
        
        Args:
            articles (list): 기사 목록 (dict 형태의 기사 객체들)
            max_articles (int): 최대 요약할 기사 수
            
        Returns:
            dict: 기사 ID를 키로, 요약을 값으로 하는 딕셔너리
        """
        if not self.initialized:
            logger.warning("Gemini API가 초기화되지 않았습니다.")
            return {}
            
        summaries = {}
        count = 0
        
        for article in articles[:max_articles]:
            article_id = article.get('id', f"article_{count}")
            title = article.get('title', 'No Title')
            content = article.get('content', '')
            
            if not content:
                logger.warning(f"기사 ID {article_id}의 내용이 없습니다.")
                continue
                
            summary = self.summarize_article(title, content)
            if summary:
                summaries[article_id] = summary
                count += 1
                
            # API 호출 사이에 짧은 딜레이 추가
            time.sleep(0.5)
            
        logger.info(f"{count}개 기사 요약 완료")
        return summaries

# 기본 사용법 예시
if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 테스트 기사
    test_article = {
        'title': 'AI 기술의 발전과 미래 전망',
        'content': '''
        인공지능(AI) 기술은 빠르게 발전하고 있으며, 다양한 산업 분야에 혁신을 가져오고 있습니다.
        특히 생성형 AI는 텍스트, 이미지, 음성 등 다양한 형태의 콘텐츠를 생성할 수 있는 능력으로 주목받고 있습니다.
        Google, OpenAI, Anthropic 등의 기업들은 더욱 강력한 AI 모델을 개발하기 위해 경쟁하고 있으며,
        이러한 기술들은 비즈니스, 의료, 교육 등 다양한 분야에서 활용되고 있습니다.
        
        전문가들은 향후 5년 내에 AI 기술이 더욱 발전하여 일상생활과 업무 방식에 큰 변화를 가져올 것으로 예측하고 있습니다.
        그러나 AI 기술의 발전과 함께 윤리적, 사회적 문제들도 제기되고 있어 균형 잡힌 발전과 규제가 필요하다는 목소리도 커지고 있습니다.
        '''
    }
    
    # Gemini 요약기 초기화
    summarizer = GeminiSummarizer()
    
    # 요약 테스트
    if summarizer.initialized:
        summary = summarizer.summarize_article(test_article['title'], test_article['content'])
        print("\n🤖 Gemini 요약 결과:")
        print(summary)
    else:
        print("\n⚠️ API 키를 설정하고 다시 시도하세요.")
