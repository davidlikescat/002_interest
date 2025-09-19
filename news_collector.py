#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 뉴스 수집기
Google News 검색 + 기사 크롤링 + 키워드 필터링을 하나의 모듈로 통합
"""

import requests
import feedparser
import time
import logging
from datetime import datetime, timedelta
from urllib.parse import quote, urljoin, urlparse
from bs4 import BeautifulSoup
import re

# 키워드 매니저 import (선택적)
try:
    from keyword_manager import KeywordManager
    KEYWORD_MANAGER_AVAILABLE = True
except ImportError:
    KEYWORD_MANAGER_AVAILABLE = False

logger = logging.getLogger(__name__)

class NewsCollector:
    """통합 뉴스 수집기 - Google News 검색부터 크롤링까지"""

    def __init__(self, max_articles=10, use_keyword_manager=True):
        self.max_articles = max_articles
        self.use_keyword_manager = use_keyword_manager and KEYWORD_MANAGER_AVAILABLE
        self.session = requests.Session()

        # 공통 헤더 설정
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })

        # 키워드 매니저 초기화
        self.keyword_manager = None
        if self.use_keyword_manager:
            try:
                self.keyword_manager = KeywordManager()
                logger.info("✅ 키워드 매니저 연결 성공")
            except Exception as e:
                logger.warning(f"키워드 매니저 초기화 실패: {e}")
                self.use_keyword_manager = False

        # AI 관련 핵심 키워드 (Fallback용)
        self.default_ai_keywords = [
            '인공지능', 'AI', '생성형AI', 'ChatGPT', 'LLM', '머신러닝', '딥러닝',
            'GPT', '자율주행', 'AI반도체', '네이버AI', '카카오AI', '삼성AI',
            '클로바', '바드', 'Bard', '구글AI', 'OpenAI', 'Claude'
        ]

        # 현재 사용할 키워드 설정
        self.ai_keywords = self._get_current_keywords()

        # 사이트별 최적화된 본문 선택자
        self.content_selectors = {
            'aitimes.com': ['.article-content', '.news-content'],
            'zdnet.co.kr': ['.view_con', '.article_view'],
            'chosun.com': ['.news_text', '.article_view'],
            'dt.co.kr': ['.article-content', '.view-con'],
            'etnews.com': ['.article_txt', '.news-content'],
            'hankyung.com': ['.article-content'],
            'mk.co.kr': ['.news_detail_text']
        }

        # 제거할 요소들
        self.remove_selectors = [
            'script', 'style', 'nav', 'header', 'footer', 'aside',
            '.advertisement', '.ad', '.ads', '.social-share',
            '.related-articles', '.comment', '.tag'
        ]

        # 통계
        self.stats = {
            'searched_articles': 0,
            'crawled_articles': 0,
            'filtered_articles': 0,
            'failed_crawls': 0,
            'keyword_matches': {}
        }

    def _get_current_keywords(self) -> list:
        """현재 사용할 키워드 가져오기"""
        if self.use_keyword_manager and self.keyword_manager:
            try:
                keywords = self.keyword_manager.get_search_keywords()
                logger.info(f"키워드 매니저에서 {len(keywords)}개 키워드 로드")
                return keywords
            except Exception as e:
                logger.warning(f"키워드 매니저에서 키워드 로드 실패: {e}")

        logger.info(f"기본 키워드 사용: {len(self.default_ai_keywords)}개")
        return self.default_ai_keywords

    def refresh_keywords(self) -> bool:
        """키워드 새로고침"""
        try:
            if self.use_keyword_manager and self.keyword_manager:
                self.ai_keywords = self.keyword_manager.get_search_keywords(use_cache=False)
                logger.info(f"키워드 새로고침 완료: {len(self.ai_keywords)}개")
                return True
            return False
        except Exception as e:
            logger.error(f"키워드 새로고침 실패: {e}")
            return False

    def get_keyword_info(self) -> dict:
        """키워드 정보 반환"""
        return {
            'total_keywords': len(self.ai_keywords),
            'keyword_manager_enabled': self.use_keyword_manager,
            'keywords_sample': self.ai_keywords[:10],
            'source': 'keyword_manager' if self.use_keyword_manager else 'default'
        }

    def collect_ai_news(self) -> list:
        """AI 뉴스 수집 메인 함수"""
        logger.info(f"AI 뉴스 수집 시작 (최대 {self.max_articles}개)")

        # 1단계: Google News에서 AI 뉴스 검색
        search_results = self._search_google_news()
        if not search_results:
            logger.warning("Google News 검색 결과가 없습니다")
            return []

        self.stats['searched_articles'] = len(search_results)
        logger.info(f"Google News 검색 완료: {len(search_results)}개 발견")

        # 2단계: 각 기사 크롤링 및 필터링
        collected_articles = []

        for i, article in enumerate(search_results[:self.max_articles], 1):
            try:
                logger.info(f"기사 처리 중 ({i}/{min(len(search_results), self.max_articles)}): {article['title'][:50]}...")

                # 기사 본문 크롤링
                content = self._crawl_article_content(article['url'])

                if content:
                    article['content'] = content
                    article['content_length'] = len(content)

                    # AI 관련성 필터링
                    if self._is_ai_related(article):
                        # 키워드 추출
                        article['found_keywords'] = self._extract_keywords(article)
                        collected_articles.append(article)
                        self.stats['filtered_articles'] += 1
                        logger.info(f"✅ AI 관련 기사 수집: {article['title'][:50]}...")
                    else:
                        logger.info(f"⏭️ AI 무관 기사 스킵: {article['title'][:50]}...")

                    self.stats['crawled_articles'] += 1
                else:
                    # 크롤링 실패해도 요약으로 포함
                    article['content'] = article.get('summary', '')
                    article['content_length'] = len(article['content'])
                    article['found_keywords'] = self._extract_keywords(article)

                    if self._is_ai_related(article):
                        collected_articles.append(article)
                        self.stats['filtered_articles'] += 1

                    self.stats['failed_crawls'] += 1

                # 요청 간격 (서버 부하 방지)
                time.sleep(1)

            except Exception as e:
                logger.error(f"기사 처리 중 오류: {e}")
                self.stats['failed_crawls'] += 1
                continue

        # 최신순 정렬
        collected_articles.sort(key=lambda x: x['published'], reverse=True)

        logger.info(f"AI 뉴스 수집 완료: {len(collected_articles)}개")
        self._print_statistics()

        return collected_articles

    def _search_google_news(self) -> list:
        """Google News RSS에서 AI 뉴스 검색"""
        try:
            # AI 핵심 키워드로 검색 쿼리 구성
            core_keywords = ['인공지능', 'AI', '생성형AI', 'ChatGPT', 'LLM']
            search_query = ' OR '.join([f'"{kw}"' for kw in core_keywords])
            search_query += ' when:1d'  # 최근 1일

            encoded_query = quote(search_query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"

            logger.info(f"Google News 검색: {rss_url}")

            # RSS 피드 가져오기
            response = self.session.get(rss_url, timeout=30)
            response.raise_for_status()

            # feedparser로 파싱
            feed = feedparser.parse(response.content)

            if not feed.entries:
                return []

            articles = []
            for entry in feed.entries[:self.max_articles * 2]:  # 여유분 확보
                try:
                    # 기사 기본 정보 추출
                    article = {
                        'title': entry.title,
                        'url': self._extract_original_url(entry.link),
                        'summary': getattr(entry, 'summary', '')[:300],
                        'source': getattr(entry, 'source', {}).get('title', 'Unknown'),
                        'published': self._parse_published_time(entry),
                        'content': '',
                        'found_keywords': []
                    }
                    articles.append(article)

                except Exception as e:
                    logger.warning(f"RSS 엔트리 파싱 실패: {e}")
                    continue

            return articles

        except Exception as e:
            logger.error(f"Google News 검색 실패: {e}")
            return []

    def _extract_original_url(self, google_news_url: str) -> str:
        """Google News URL에서 원본 기사 URL 추출"""
        try:
            if 'news.google.com' not in google_news_url:
                return google_news_url

            # 리다이렉트 따라가기
            response = self.session.head(google_news_url, allow_redirects=True, timeout=10)
            return response.url

        except Exception:
            return google_news_url

    def _parse_published_time(self, entry) -> datetime:
        """RSS 엔트리에서 발행 시간 파싱"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6])
        except Exception:
            pass
        return datetime.now()

    def _crawl_article_content(self, url: str) -> str:
        """기사 본문 크롤링"""
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()

            # 인코딩 설정
            if response.encoding.lower() in ['iso-8859-1', 'ascii']:
                response.encoding = 'utf-8'

            soup = BeautifulSoup(response.content, 'html.parser')

            # 본문 추출
            content = self._extract_main_content(soup, url)
            return self._clean_text(content)

        except Exception as e:
            logger.warning(f"크롤링 실패 ({url}): {e}")
            return ""

    def _extract_main_content(self, soup: BeautifulSoup, url: str) -> str:
        """메인 컨텐츠 추출"""
        domain = urlparse(url).netloc.lower()

        # 사이트별 최적화된 선택자 사용
        selectors = []
        for site_domain, site_selectors in self.content_selectors.items():
            if site_domain in domain:
                selectors = site_selectors
                break

        # 기본 선택자
        if not selectors:
            selectors = [
                'article', '.article-content', '.news-content', '.post-content',
                '.entry-content', '.article-body', '.content', '.main-content'
            ]

        # 선택자별로 시도
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # 불필요한 요소 제거
                for remove_selector in self.remove_selectors:
                    for tag in element.select(remove_selector):
                        tag.decompose()

                text = element.get_text(separator=' ', strip=True)
                if len(text) > 200:  # 최소 길이 확인
                    return text

        # 폴백: p 태그들 수집
        paragraphs = soup.find_all('p')
        if paragraphs:
            return ' '.join([p.get_text(strip=True) for p in paragraphs])

        return ""

    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        if not text:
            return ""

        # HTML 엔티티 디코딩
        import html
        text = html.unescape(text)

        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)

        # 특수 문자 정리
        text = text.replace('\u200b', '').replace('\ufeff', '')

        return text.strip()

    def _is_ai_related(self, article: dict) -> bool:
        """기사가 AI 관련인지 확인"""
        text_to_check = f"{article['title']} {article['content']} {article['summary']}".lower()

        # AI 키워드 존재 확인
        for keyword in self.ai_keywords:
            if keyword.lower() in text_to_check:
                return True

        return False

    def _extract_keywords(self, article: dict) -> list:
        """기사에서 발견된 키워드 추출 및 통계 업데이트"""
        text_to_check = f"{article['title']} {article['content']}".lower()
        found_keywords = []

        for keyword in self.ai_keywords:
            if keyword.lower() in text_to_check:
                found_keywords.append(keyword)

                # 키워드 매치 통계 업데이트
                if keyword not in self.stats['keyword_matches']:
                    self.stats['keyword_matches'][keyword] = 0
                self.stats['keyword_matches'][keyword] += 1

                # 키워드 매니저에 사용량 업데이트
                if self.use_keyword_manager and self.keyword_manager:
                    try:
                        self.keyword_manager.update_usage(keyword, 1)
                    except Exception as e:
                        logger.warning(f"키워드 사용량 업데이트 실패 ({keyword}): {e}")

        return found_keywords[:5]  # 최대 5개

    def _print_statistics(self):
        """수집 통계 출력"""
        print(f"\n📊 뉴스 수집 통계:")
        print(f"  • 검색된 기사: {self.stats['searched_articles']}개")
        print(f"  • 크롤링 성공: {self.stats['crawled_articles']}개")
        print(f"  • AI 관련 필터링: {self.stats['filtered_articles']}개")
        print(f"  • 크롤링 실패: {self.stats['failed_crawls']}개")

        if self.stats['searched_articles'] > 0:
            success_rate = (self.stats['crawled_articles'] / self.stats['searched_articles']) * 100
            print(f"  • 크롤링 성공률: {success_rate:.1f}%")

        # 키워드 매니저 정보
        print(f"\n🔑 키워드 정보:")
        keyword_info = self.get_keyword_info()
        print(f"  • 총 키워드: {keyword_info['total_keywords']}개")
        print(f"  • 키워드 소스: {keyword_info['source']}")

        if self.stats['keyword_matches']:
            print(f"  • 매치된 키워드: {len(self.stats['keyword_matches'])}개")
            top_keywords = sorted(
                self.stats['keyword_matches'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            for keyword, count in top_keywords:
                print(f"    - {keyword}: {count}회")
        else:
            print(f"  • 매치된 키워드: 없음")

    def get_statistics(self) -> dict:
        """통계 정보 반환"""
        return self.stats.copy()


def test_collector():
    """뉴스 수집기 테스트"""
    print("🧪 뉴스 수집기 테스트 (키워드 매니저 통합)")
    print("=" * 50)

    # 키워드 매니저 연동 테스트
    collector = NewsCollector(max_articles=3, use_keyword_manager=True)

    # 키워드 정보 출력
    keyword_info = collector.get_keyword_info()
    print(f"🔑 키워드 매니저: {'✅ 연결됨' if keyword_info['keyword_manager_enabled'] else '❌ 미연결'}")
    print(f"📝 사용 키워드: {keyword_info['total_keywords']}개 ({keyword_info['source']})")
    print(f"📋 키워드 예시: {', '.join(keyword_info['keywords_sample'][:5])}")

    print(f"\n📰 뉴스 수집 시작...")
    articles = collector.collect_ai_news()

    if articles:
        print(f"\n✅ {len(articles)}개 기사 수집 성공:")
        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title']}")
            print(f"   출처: {article['source']}")
            print(f"   발행: {article['published'].strftime('%Y-%m-%d %H:%M')}")
            print(f"   키워드: {', '.join(article['found_keywords'])}")
            print(f"   본문: {len(article['content'])}자")
            print()

        # 키워드 매니저 통계 (가능한 경우)
        if collector.use_keyword_manager and collector.keyword_manager:
            try:
                stats = collector.keyword_manager.get_statistics(days=1)
                print(f"\n📈 키워드 매니저 통계 (최근 1일):")
                print(f"  • 총 검색: {stats['total_searches']}회")
                print(f"  • 매치된 기사: {stats['total_articles']}개")
                print(f"  • 활성 키워드: {stats['unique_keywords']}개")
            except Exception as e:
                logger.warning(f"키워드 매니저 통계 가져오기 실패: {e}")

    else:
        print("❌ 기사 수집 실패")


if __name__ == "__main__":
    test_collector()