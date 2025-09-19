#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간소화된 Notion 저장 관리자
복잡한 블록 구조 없이 효율적인 Notion 페이지 생성
"""

import requests
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class StorageManager:
    """간소화된 Notion 저장 관리자"""

    def __init__(self):
        self.api_key = os.getenv('NOTION_API_KEY')
        self.database_id = os.getenv('NOTION_DATABASE_ID')

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }

    def save_news_to_notion(self, articles: List[Dict]) -> Optional[str]:
        """뉴스 기사들을 Notion에 저장"""
        if not self.api_key or not self.database_id:
            logger.error("Notion API 설정이 누락되었습니다")
            return None

        if not articles:
            logger.warning("저장할 기사가 없습니다")
            return None

        try:
            # 페이지 생성
            page_url = self._create_news_page(articles)

            if page_url:
                logger.info(f"Notion 저장 완료: {page_url}")
                return page_url
            else:
                logger.error("Notion 페이지 생성 실패")
                return None

        except Exception as e:
            logger.error(f"Notion 저장 중 오류: {e}")
            return None

    def _create_news_page(self, articles: List[Dict]) -> Optional[str]:
        """뉴스 페이지 생성"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.now().strftime('%H:%M')

            # 페이지 제목
            title = f"🤖 AI News - {today} {current_time}"

            # 기본 페이지 데이터
            page_data = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Name": {  # Notion의 기본 제목 속성
                        "title": [
                            {
                                "type": "text",
                                "text": {"content": title}
                            }
                        ]
                    }
                }
            }

            # 추가 속성들 (있으면 추가)
            self._add_optional_properties(page_data, articles, today)

            # 페이지 생성 API 호출
            url = "https://api.notion.com/v1/pages"
            response = requests.post(url, headers=self.headers, json=page_data, timeout=30)

            if response.status_code == 200:
                page_result = response.json()
                page_url = page_result.get('url', '')

                # 페이지 내용 추가
                if page_result.get('id'):
                    self._add_page_content(page_result['id'], articles)

                return page_url
            else:
                logger.error(f"페이지 생성 실패: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"페이지 생성 중 오류: {e}")
            return None

    def _add_optional_properties(self, page_data: Dict, articles: List[Dict], date: str):
        """선택적 속성들 추가 (오류가 발생해도 무시)"""
        try:
            # 날짜 속성
            page_data["properties"]["Date"] = {
                "date": {"start": date}
            }

            # 기사 수
            page_data["properties"]["Articles"] = {
                "number": len(articles)
            }

            # 카테고리
            page_data["properties"]["Category"] = {
                "select": {"name": "AI News"}
            }

            # 상태
            page_data["properties"]["Status"] = {
                "select": {"name": "Published"}
            }

        except Exception as e:
            logger.warning(f"선택적 속성 추가 중 오류 (무시됨): {e}")

    def _add_page_content(self, page_id: str, articles: List[Dict]):
        """페이지에 기사 내용 추가"""
        try:
            blocks = self._build_content_blocks(articles)

            # 블록을 100개씩 나누어 추가
            chunk_size = 100
            for i in range(0, len(blocks), chunk_size):
                chunk = blocks[i:i + chunk_size]
                self._add_blocks_to_page(page_id, chunk)

        except Exception as e:
            logger.warning(f"페이지 내용 추가 중 오류: {e}")

    def _build_content_blocks(self, articles: List[Dict]) -> List[Dict]:
        """콘텐츠 블록 구성"""
        blocks = []

        # 헤더
        blocks.append({
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": f"🤖 AI 뉴스 모음 ({len(articles)}개)"}
                    }
                ]
            }
        })

        # 요약 정보
        summary_text = self._generate_summary(articles)
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": summary_text}
                    }
                ]
            }
        })

        # 구분선
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })

        # 각 기사 추가
        for i, article in enumerate(articles, 1):
            # 기사 제목
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"{i}. {article['title']}"}
                        }
                    ]
                }
            })

            # 메타 정보
            meta_text = f"📰 {article['source']} | ⏰ {article['published'].strftime('%Y-%m-%d %H:%M')} | 🏷️ {', '.join(article.get('found_keywords', []))}"
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": meta_text}
                        }
                    ]
                }
            })

            # 첫 문장 또는 요약
            preview_text = self._get_article_preview(article)
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"💡 {preview_text}"}
                        }
                    ]
                }
            })

            # 기사 링크 (북마크)
            if article.get('url'):
                blocks.append({
                    "object": "block",
                    "type": "bookmark",
                    "bookmark": {
                        "url": article['url']
                    }
                })

            # 기사 간 구분선 (마지막 기사 제외)
            if i < len(articles):
                blocks.append({
                    "object": "block",
                    "type": "divider",
                    "divider": {}
                })

        # 푸터
        blocks.extend(self._build_footer_blocks())

        return blocks

    def _generate_summary(self, articles: List[Dict]) -> str:
        """기사 모음 요약 생성"""
        # 언론사 통계
        sources = {}
        all_keywords = []

        for article in articles:
            source = article.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
            all_keywords.extend(article.get('found_keywords', []))

        # 주요 키워드 (빈도순)
        keyword_count = {}
        for kw in all_keywords:
            keyword_count[kw] = keyword_count.get(kw, 0) + 1

        top_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:5]
        keyword_text = ', '.join([f"{kw}({count})" for kw, count in top_keywords])

        summary = f"""📊 수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📰 언론사: {len(sources)}곳 ({', '.join(list(sources.keys())[:3])}{"..." if len(sources) > 3 else ""})
🏷️ 주요 키워드: {keyword_text}
📄 평균 본문 길이: {sum(article.get('content_length', 0) for article in articles) // len(articles)}자"""

        return summary

    def _get_article_preview(self, article: Dict) -> str:
        """기사 미리보기 텍스트 생성"""
        content = article.get('content', '')

        if content:
            # 첫 문장 추출
            sentences = content.split('.')
            first_sentence = sentences[0].strip()

            if len(first_sentence) < 30 and len(sentences) > 1:
                first_sentence = f"{first_sentence}. {sentences[1].strip()}"

            # 길이 제한
            if len(first_sentence) > 150:
                first_sentence = first_sentence[:150] + "..."

            return first_sentence

        # 콘텐츠가 없으면 요약 사용
        summary = article.get('summary', '')
        if summary:
            return summary[:150] + ("..." if len(summary) > 150 else "")

        return "기사 내용을 확인할 수 없습니다."

    def _build_footer_blocks(self) -> List[Dict]:
        """푸터 블록 생성"""
        blocks = []

        # 시스템 정보
        blocks.append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "🤖 시스템 정보"}
                    }
                ]
            }
        })

        system_info = f"""• 개발자: JoonmoYang
• 시스템: Google News AI Agent v2.0 (Simplified)
• 기술: Python + Google News RSS + Notion API
• 처리: 뉴스 검색 → 크롤링 → 필터링 → Notion 저장
• 특징: OpenAI API 비용 없음, 간소화된 구조"""

        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": system_info}
                    }
                ]
            }
        })

        return blocks

    def _add_blocks_to_page(self, page_id: str, blocks: List[Dict]):
        """페이지에 블록 추가"""
        try:
            url = f"https://api.notion.com/v1/blocks/{page_id}/children"
            response = requests.patch(
                url,
                headers=self.headers,
                json={"children": blocks},
                timeout=30
            )

            if response.status_code == 200:
                logger.info(f"블록 {len(blocks)}개 추가 성공")
            else:
                logger.warning(f"블록 추가 실패: {response.status_code}")

        except Exception as e:
            logger.warning(f"블록 추가 중 오류: {e}")

    def test_connection(self) -> bool:
        """Notion 연결 테스트"""
        if not self.api_key or not self.database_id:
            print("❌ Notion API 설정이 누락되었습니다")
            return False

        try:
            # 데이터베이스 정보 조회
            url = f"https://api.notion.com/v1/databases/{self.database_id}"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                db_info = response.json()
                print(f"✅ Notion 연결 성공: {db_info.get('title', [{}])[0].get('plain_text', 'Unknown')}")
                return True
            else:
                print(f"❌ Notion 연결 실패: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Notion 연결 테스트 오류: {e}")
            return False


def test_storage_manager():
    """저장 관리자 테스트"""
    print("🧪 Notion 저장 관리자 테스트")
    print("=" * 50)

    storage = StorageManager()

    # 연결 테스트
    if not storage.test_connection():
        return False

    # 테스트 데이터
    test_articles = [
        {
            'title': 'ChatGPT 신기능 출시',
            'source': '테크뉴스',
            'published': datetime.now(),
            'url': 'https://example.com/article1',
            'content': 'OpenAI가 ChatGPT의 새로운 기능을 발표했습니다.',
            'content_length': 100,
            'found_keywords': ['ChatGPT', 'OpenAI']
        },
        {
            'title': '구글 AI 발전',
            'source': 'AI타임즈',
            'published': datetime.now(),
            'url': 'https://example.com/article2',
            'content': '구글이 새로운 AI 모델을 개발했다고 발표했습니다.',
            'content_length': 120,
            'found_keywords': ['AI', '구글']
        }
    ]

    # 저장 테스트
    page_url = storage.save_news_to_notion(test_articles)

    if page_url:
        print(f"✅ 테스트 성공: {page_url}")
        return True
    else:
        print("❌ 테스트 실패")
        return False


if __name__ == "__main__":
    test_storage_manager()