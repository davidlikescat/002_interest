#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Sheets 기반 키워드 관리자
동적 키워드 로딩으로 실시간 키워드 변경 지원
"""

import os
import logging
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

try:
    import gspread
    from google.auth.exceptions import RefreshError, GoogleAuthError
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

logger = logging.getLogger(__name__)

class KeywordManager:
    """Google Sheets 기반 동적 키워드 관리자"""

    def __init__(self, credentials_file: str = "credentials.json",
                 spreadsheet_name: str = "Google News AI Keywords"):
        """
        키워드 매니저 초기화

        Args:
            credentials_file: Google Sheets API 인증 파일 경로
            spreadsheet_name: 구글 스프레드시트 이름
        """
        # 환경변수 또는 기본값 사용
        self.credentials_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE', credentials_file)
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        self.spreadsheet_name = os.getenv('GOOGLE_SHEETS_SPREADSHEET_NAME', spreadsheet_name)
        self.worksheet_name = os.getenv('GOOGLE_SHEETS_WORKSHEET_NAME', '키워드목록')

        # 캐시 설정
        self.cache_duration = int(os.getenv('KEYWORD_CACHE_DURATION', '300'))  # 5분
        self._cached_keywords = {}
        self._cache_expiry = None

        # 기본 키워드 (Fallback용)
        self.default_keywords = [
            '인공지능', 'AI', '생성형AI', 'ChatGPT', 'LLM', '머신러닝', '딥러닝',
            'GPT', '자율주행', 'AI반도체', '네이버AI', '카카오AI', '삼성AI',
            '클로바', '바드', 'Bard', '구글AI', 'OpenAI', 'Claude', '알렉사', '시리'
        ]

        # Google Sheets 클라이언트
        self.gc = None
        self.spreadsheet = None
        self.sheets_available = False

        # 워크시트 이름들
        self.SHEET_NAMES = {
            'keywords': '키워드목록',
            'categories': '카테고리',
            'statistics': '통계',
            'settings': '설정'
        }

        # 통계 데이터
        self.usage_stats = {}

        # 초기화 시도
        self._initialize_sheets_client()

    def _initialize_sheets_client(self):
        """Google Sheets 클라이언트 초기화"""
        if not GSPREAD_AVAILABLE:
            logger.warning("gspread 라이브러리가 설치되지 않았습니다")
            return False

        if not os.path.exists(self.credentials_file):
            logger.warning(f"Google Sheets 인증 파일을 찾을 수 없습니다: {self.credentials_file}")
            return False

        try:
            # Service Account 인증
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=scopes
            )

            self.gc = gspread.authorize(credentials)

            # 스프레드시트 열기 또는 생성
            try:
                if self.spreadsheet_id:
                    self.spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
                else:
                    self.spreadsheet = self.gc.open(self.spreadsheet_name)

                logger.info(f"기존 스프레드시트 열기: {self.spreadsheet.title}")
            except gspread.SpreadsheetNotFound:
                logger.info(f"스프레드시트 생성 중: {self.spreadsheet_name}")
                self.spreadsheet = self.gc.create(self.spreadsheet_name)
                self._setup_default_sheets()

            self.sheets_available = True
            logger.info("✅ Google Sheets 클라이언트 초기화 성공")
            return True

        except GoogleAuthError as e:
            logger.error(f"Google 인증 오류: {e}")
            self.sheets_available = False
            return False
        except Exception as e:
            logger.error(f"Google Sheets 클라이언트 초기화 실패: {e}")
            self.sheets_available = False
            return False

    def _setup_default_sheets(self):
        """기본 워크시트 구조 설정"""
        try:
            # 기본 시트 제거
            try:
                default_sheet = self.spreadsheet.sheet1
                self.spreadsheet.del_worksheet(default_sheet)
            except:
                pass

            # 키워드 목록 시트
            keywords_sheet = self.spreadsheet.add_worksheet(
                title=self.SHEET_NAMES['keywords'], rows=200, cols=10
            )

            # 헤더 설정
            keywords_headers = [
                'ID', '키워드', '카테고리', '우선순위', '활성화',
                '생성일', '수정일', '사용횟수', '설명', '비고'
            ]
            keywords_sheet.append_row(keywords_headers)

            # 기본 키워드 추가
            for i, keyword in enumerate(self.default_keywords, 1):
                row = [
                    i, keyword, 'AI기본', 5, 'TRUE',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    0, f'{keyword} 관련 뉴스 검색', ''
                ]
                keywords_sheet.append_row(row)

            # 카테고리 시트
            categories_sheet = self.spreadsheet.add_worksheet(
                title=self.SHEET_NAMES['categories'], rows=50, cols=5
            )

            categories_headers = ['카테고리명', '설명', '색상', '생성일', '활성화']
            categories_sheet.append_row(categories_headers)

            # 기본 카테고리
            default_categories = [
                ['AI기본', 'AI 기본 키워드', '#4285F4', datetime.now().strftime('%Y-%m-%d'), 'TRUE'],
                ['생성AI', '생성형 AI 관련', '#34A853', datetime.now().strftime('%Y-%m-%d'), 'TRUE'],
                ['기업AI', '기업별 AI 서비스', '#FBBC04', datetime.now().strftime('%Y-%m-%d'), 'TRUE'],
                ['AI기술', 'AI 기술 및 연구', '#EA4335', datetime.now().strftime('%Y-%m-%d'), 'TRUE']
            ]

            for category in default_categories:
                categories_sheet.append_row(category)

            # 통계 시트
            stats_sheet = self.spreadsheet.add_worksheet(
                title=self.SHEET_NAMES['statistics'], rows=100, cols=8
            )

            stats_headers = [
                '날짜', '키워드', '검색횟수', '매치된기사수',
                '평균관련도', '최고관련도', '카테고리', '비고'
            ]
            stats_sheet.append_row(stats_headers)

            # 설정 시트
            settings_sheet = self.spreadsheet.add_worksheet(
                title=self.SHEET_NAMES['settings'], rows=20, cols=3
            )

            settings_headers = ['설정명', '값', '설명']
            settings_sheet.append_row(settings_headers)

            # 기본 설정
            default_settings = [
                ['캐시_지속시간_분', '5', '키워드 캐시 지속 시간 (분)'],
                ['최대_키워드수', '50', '한 번에 로드할 최대 키워드 수'],
                ['자동_업데이트', 'TRUE', '키워드 사용 통계 자동 업데이트'],
                ['우선순위_임계값', '3', '사용할 키워드 최소 우선순위'],
                ['최신_업데이트', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '마지막 업데이트 시간']
            ]

            for setting in default_settings:
                settings_sheet.append_row(setting)

            logger.info("기본 워크시트 구조 설정 완료")

        except Exception as e:
            logger.error(f"기본 시트 설정 실패: {e}")

    def get_keywords(self, category: Optional[str] = None,
                    min_priority: int = 1, force_refresh: bool = False) -> List[str]:
        """
        활성화된 키워드 목록 가져오기

        Args:
            category: 특정 카테고리 키워드만 가져오기 (None=전체)
            min_priority: 최소 우선순위 (1-10)
            force_refresh: 캐시 무시하고 강제 새로고침

        Returns:
            키워드 리스트
        """
        try:
            # 캐시 확인
            cache_key = f"{category}_{min_priority}"

            if not force_refresh and self._is_cache_valid() and cache_key in self._cached_keywords:
                logger.debug(f"캐시에서 키워드 반환: {len(self._cached_keywords[cache_key])}개")
                return self._cached_keywords[cache_key]

            # Google Sheets에서 키워드 로드
            keywords = self._load_keywords_from_sheets(category, min_priority)

            if keywords:
                # 캐시 업데이트
                self._cached_keywords[cache_key] = keywords
                self._cache_expiry = datetime.now() + timedelta(seconds=self.cache_duration)

                logger.info(f"Google Sheets에서 키워드 로드: {len(keywords)}개")
                return keywords
            else:
                # 폴백: 기본 키워드 사용
                logger.warning("Google Sheets에서 키워드를 가져올 수 없어 기본 키워드 사용")
                return self.default_keywords

        except Exception as e:
            logger.error(f"키워드 가져오기 실패: {e}")
            return self.default_keywords

    def _load_keywords_from_sheets(self, category: Optional[str], min_priority: int) -> List[str]:
        """Google Sheets에서 키워드 로드"""
        try:
            if not self.spreadsheet or not self.sheets_available:
                return []

            # 키워드 시트 가져오기
            try:
                keywords_sheet = self.spreadsheet.worksheet(self.SHEET_NAMES['keywords'])
            except gspread.WorksheetNotFound:
                logger.error(f"키워드 워크시트를 찾을 수 없습니다: {self.SHEET_NAMES['keywords']}")
                return []

            # 모든 데이터 가져오기
            records = keywords_sheet.get_all_records()

            if not records:
                return []

            keywords = []

            for record in records:
                try:
                    # 활성화 확인
                    if str(record.get('활성화', '')).upper() != 'TRUE':
                        continue

                    # 우선순위 확인
                    priority = int(record.get('우선순위', 0))
                    if priority < min_priority:
                        continue

                    # 카테고리 필터
                    if category and record.get('카테고리', '') != category:
                        continue

                    keyword = record.get('키워드', '').strip()
                    if keyword:
                        keywords.append(keyword)

                except (ValueError, TypeError) as e:
                    logger.warning(f"키워드 레코드 파싱 실패: {e}")
                    continue

            return keywords

        except Exception as e:
            logger.error(f"Sheets에서 키워드 로드 실패: {e}")
            return []

    def get_search_keywords(self, use_cache: bool = True) -> List[str]:
        """검색용 키워드 반환 (기본 우선순위로)"""
        return self.get_keywords(min_priority=3, force_refresh=not use_cache)

    def add_keyword(self, keyword: str, category: str = "사용자추가",
                   priority: int = 5, description: str = "") -> bool:
        """
        새 키워드 추가

        Args:
            keyword: 추가할 키워드
            category: 카테고리
            priority: 우선순위 (1-10)
            description: 설명

        Returns:
            성공 여부
        """
        try:
            if not self.spreadsheet or not self.sheets_available:
                logger.error("Google Sheets 연결이 없습니다")
                return False

            keywords_sheet = self.spreadsheet.worksheet(self.SHEET_NAMES['keywords'])

            # 중복 확인
            existing_keywords = [record.get('키워드', '') for record in keywords_sheet.get_all_records()]
            if keyword in existing_keywords:
                logger.warning(f"키워드가 이미 존재합니다: {keyword}")
                return False

            # 새 ID 생성
            records = keywords_sheet.get_all_records()
            next_id = len(records) + 1

            # 새 키워드 추가
            new_row = [
                next_id, keyword, category, priority, 'TRUE',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                0, description, ''
            ]

            keywords_sheet.append_row(new_row)

            # 캐시 무효화
            self._clear_cache()

            logger.info(f"키워드 추가 완료: {keyword}")
            return True

        except Exception as e:
            logger.error(f"키워드 추가 실패: {e}")
            return False

    def update_keyword_usage(self, keyword: str, matched_articles: int = 1) -> bool:
        """
        키워드 사용 통계 업데이트

        Args:
            keyword: 키워드
            matched_articles: 매치된 기사 수

        Returns:
            성공 여부
        """
        try:
            if not self.spreadsheet or not self.sheets_available:
                return False

            # 로컬 통계 업데이트
            if keyword not in self.usage_stats:
                self.usage_stats[keyword] = {'usage_count': 0, 'matched_articles': 0}

            self.usage_stats[keyword]['usage_count'] += 1
            self.usage_stats[keyword]['matched_articles'] += matched_articles

            # Google Sheets 업데이트 (비동기적으로)
            self._update_sheets_statistics(keyword, matched_articles)

            return True

        except Exception as e:
            logger.error(f"키워드 사용 통계 업데이트 실패: {e}")
            return False

    def _update_sheets_statistics(self, keyword: str, matched_articles: int):
        """Google Sheets 통계 업데이트 (백그라운드)"""
        try:
            # 키워드 시트에서 사용횟수 업데이트
            keywords_sheet = self.spreadsheet.worksheet(self.SHEET_NAMES['keywords'])
            records = keywords_sheet.get_all_records()

            for i, record in enumerate(records, 2):  # 2부터 시작 (헤더 제외)
                if record.get('키워드') == keyword:
                    current_usage = int(record.get('사용횟수', 0))
                    new_usage = current_usage + 1

                    # 사용횟수와 수정일 업데이트
                    keywords_sheet.update(f'H{i}', new_usage)  # 사용횟수 컬럼
                    keywords_sheet.update(f'G{i}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))  # 수정일
                    break

            # 통계 시트에 기록 추가
            stats_sheet = self.spreadsheet.worksheet(self.SHEET_NAMES['statistics'])

            stats_row = [
                datetime.now().strftime('%Y-%m-%d'),
                keyword,
                1,  # 검색횟수
                matched_articles,
                0,  # 평균관련도 (추후 구현)
                0,  # 최고관련도 (추후 구현)
                '',  # 카테고리
                f'자동 업데이트 - {datetime.now().strftime("%H:%M:%S")}'
            ]

            stats_sheet.append_row(stats_row)

        except Exception as e:
            logger.warning(f"Google Sheets 통계 업데이트 실패: {e}")

    def get_keyword_categories(self) -> List[Dict[str, str]]:
        """활성화된 카테고리 목록 가져오기"""
        try:
            if not self.spreadsheet or not self.sheets_available:
                return []

            categories_sheet = self.spreadsheet.worksheet(self.SHEET_NAMES['categories'])
            records = categories_sheet.get_all_records()

            categories = []
            for record in records:
                if str(record.get('활성화', '')).upper() == 'TRUE':
                    categories.append({
                        'name': record.get('카테고리명', ''),
                        'description': record.get('설명', ''),
                        'color': record.get('색상', '#000000')
                    })

            return categories

        except Exception as e:
            logger.error(f"카테고리 가져오기 실패: {e}")
            return []

    def _is_cache_valid(self) -> bool:
        """캐시 유효성 확인"""
        return self._cache_expiry and datetime.now() < self._cache_expiry

    def _clear_cache(self):
        """캐시 무효화"""
        self._cached_keywords.clear()
        self._cache_expiry = None

    def refresh_cache(self):
        """키워드 캐시 강제 갱신"""
        logger.info("키워드 캐시 강제 갱신")
        self._clear_cache()
        return self.get_keywords(force_refresh=True)

    def get_priority_keywords(self, max_count: int = 5) -> List[str]:
        """우선순위 키워드 반환"""
        return self.get_keywords(min_priority=8, force_refresh=False)[:max_count]

    def get_statistics(self, days: int = 7) -> Dict:
        """키워드 사용 통계 가져오기"""
        try:
            if not self.spreadsheet or not self.sheets_available:
                return self._get_local_statistics()

            stats_sheet = self.spreadsheet.worksheet(self.SHEET_NAMES['statistics'])
            records = stats_sheet.get_all_records()

            # 최근 N일 데이터 필터링
            cutoff_date = datetime.now() - timedelta(days=days)

            keyword_stats = {}
            total_searches = 0
            total_articles = 0

            for record in records:
                try:
                    record_date = datetime.strptime(record.get('날짜', ''), '%Y-%m-%d')
                    if record_date < cutoff_date:
                        continue

                    keyword = record.get('키워드', '')
                    searches = int(record.get('검색횟수', 0))
                    articles = int(record.get('매치된기사수', 0))

                    if keyword not in keyword_stats:
                        keyword_stats[keyword] = {'searches': 0, 'articles': 0}

                    keyword_stats[keyword]['searches'] += searches
                    keyword_stats[keyword]['articles'] += articles

                    total_searches += searches
                    total_articles += articles

                except (ValueError, TypeError):
                    continue

            # 상위 키워드 정렬
            top_keywords = sorted(
                keyword_stats.items(),
                key=lambda x: x[1]['articles'],
                reverse=True
            )[:10]

            return {
                'period_days': days,
                'total_searches': total_searches,
                'total_articles': total_articles,
                'unique_keywords': len(keyword_stats),
                'top_keywords': top_keywords,
                'average_articles_per_keyword': total_articles / len(keyword_stats) if keyword_stats else 0,
                'sheets_connected': True
            }

        except Exception as e:
            logger.error(f"통계 가져오기 실패: {e}")
            return self._get_local_statistics()

    def _get_local_statistics(self) -> Dict:
        """로컬 통계 반환 (폴백)"""
        total_usage = sum(stat['usage_count'] for stat in self.usage_stats.values())
        total_articles = sum(stat['matched_articles'] for stat in self.usage_stats.values())

        top_keywords = sorted(
            self.usage_stats.items(),
            key=lambda x: x[1]['matched_articles'],
            reverse=True
        )[:10]

        return {
            'period_days': 'session',
            'total_searches': total_usage,
            'total_articles': total_articles,
            'unique_keywords': len(self.usage_stats),
            'top_keywords': top_keywords,
            'average_articles_per_keyword': total_articles / len(self.usage_stats) if self.usage_stats else 0,
            'sheets_connected': False
        }

    def test_connection(self) -> bool:
        """Google Sheets 연결 테스트"""
        try:
            if not self.spreadsheet or not self.sheets_available:
                logger.error("Google Sheets 연결이 없습니다")
                return False

            # 키워드 시트 접근 테스트
            keywords_sheet = self.spreadsheet.worksheet(self.SHEET_NAMES['keywords'])
            test_data = keywords_sheet.get('A1:B2')

            logger.info("Google Sheets 연결 테스트 성공")
            return True

        except Exception as e:
            logger.error(f"Google Sheets 연결 테스트 실패: {e}")
            return False

    def print_status(self):
        """키워드 매니저 상태 출력"""
        print("\n📊 키워드 매니저 상태:")
        print("=" * 50)

        try:
            if not self.spreadsheet:
                print("❌ Google Sheets 연결 없음")
                print(f"📋 기본 키워드 사용: {len(self.default_keywords)}개")
                return

            print(f"✅ 스프레드시트: {self.spreadsheet.title}")
            print(f"🔗 URL: {self.spreadsheet.url}")

            # 키워드 통계
            keywords = self.get_keywords()
            print(f"📝 총 키워드 수: {len(keywords)}개")

            # 카테고리 통계
            categories = self.get_keyword_categories()
            print(f"📂 카테고리 수: {len(categories)}개")

            # 캐시 상태
            cache_status = "유효" if self._is_cache_valid() else "만료됨"
            print(f"💾 캐시 상태: {cache_status}")

            # 최근 통계
            stats = self.get_statistics(days=7)
            if stats:
                print(f"📈 최근 7일 검색: {stats['total_searches']}회")
                print(f"📰 매치된 기사: {stats['total_articles']}개")

        except Exception as e:
            print(f"❌ 상태 확인 실패: {e}")

    # 뉴스 수집기와의 통합을 위한 호환성 메서드들
    def get_ai_keywords(self) -> List[str]:
        """AI 키워드 반환 (뉴스 수집기 호환성)"""
        return self.get_keywords(category="AI기본")

    def get_all_keywords(self) -> List[str]:
        """모든 활성 키워드 반환"""
        return self.get_keywords()

    def update_usage(self, keyword: str, article_count: int = 1):
        """사용량 업데이트 (간단한 인터페이스)"""
        self.update_keyword_usage(keyword, article_count)


def test_keyword_manager():
    """키워드 매니저 테스트"""
    print("🧪 Google Sheets 키워드 매니저 테스트")
    print("=" * 50)

    try:
        # 키워드 매니저 초기화
        manager = KeywordManager()

        # 연결 테스트
        if not manager.test_connection():
            print("❌ Google Sheets 연결 실패")
            print("💡 기본 키워드로 동작합니다")

            # 기본 키워드 표시
            print(f"\n📋 기본 키워드 ({len(manager.default_keywords)}개):")
            for i, keyword in enumerate(manager.default_keywords[:10], 1):
                print(f"  {i}. {keyword}")
            return False

        print("✅ Google Sheets 연결 성공")

        # 키워드 가져오기 테스트
        keywords = manager.get_keywords()
        print(f"✅ 키워드 로드: {len(keywords)}개")

        # 상위 5개 키워드 출력
        print(f"\n📝 로드된 키워드 (상위 5개):")
        for i, keyword in enumerate(keywords[:5], 1):
            print(f"  {i}. {keyword}")

        # 카테고리 테스트
        categories = manager.get_keyword_categories()
        print(f"\n📂 카테고리: {len(categories)}개")
        for cat in categories:
            print(f"  • {cat['name']}: {cat['description']}")

        # 우선순위 키워드 테스트
        priority_keywords = manager.get_priority_keywords(3)
        print(f"\n🎯 우선순위 키워드:")
        for i, keyword in enumerate(priority_keywords, 1):
            print(f"  {i}. {keyword}")

        # 상태 출력
        manager.print_status()

        print("\n🎉 키워드 매니저 테스트 완료!")
        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False


def setup_keyword_manager():
    """키워드 매니저 설정 가이드"""
    print("🔧 Google Sheets 키워드 매니저 설정 가이드")
    print("=" * 50)
    print("1. Google Cloud Console에서 프로젝트 생성")
    print("2. Google Sheets API 및 Google Drive API 활성화")
    print("3. 서비스 계정 생성 및 JSON 키 파일 다운로드")
    print("4. credentials.json 파일명으로 저장")
    print("5. 구글 스프레드시트 생성 후 서비스 계정에 편집 권한 부여")
    print("\n💡 자세한 설정 방법:")
    print("   - Google Cloud Console: https://console.cloud.google.com/")
    print("   - API 라이브러리에서 Google Sheets API 검색 후 사용 설정")
    print("   - 사용자 인증 정보 > 서비스 계정 > 키 생성")
    print("\n🔑 환경변수 설정 (선택사항):")
    print("   - GOOGLE_SHEETS_CREDENTIALS_FILE: 인증파일 경로")
    print("   - GOOGLE_SHEETS_SPREADSHEET_NAME: 스프레드시트 이름")
    print("   - GOOGLE_SHEETS_SPREADSHEET_ID: 스프레드시트 ID")
    print("   - KEYWORD_CACHE_DURATION: 캐시 지속시간 (초)")


def create_sample_spreadsheet():
    """샘플 스프레드시트 생성 데모"""
    print("📊 샘플 키워드 스프레드시트 생성")
    print("=" * 50)

    try:
        manager = KeywordManager()

        if not manager.sheets_available:
            print("❌ Google Sheets가 설정되지 않았습니다")
            print("💡 설정 가이드를 실행하세요: python keyword_manager.py setup")
            return False

        # 스프레드시트가 없으면 생성
        if not manager.spreadsheet:
            print("📝 새 스프레드시트 생성 중...")
            manager._setup_default_sheets()

        print("✅ 샘플 스프레드시트 생성 완료!")
        print(f"🔗 URL: {manager.spreadsheet.url}")

        return True

    except Exception as e:
        print(f"❌ 샘플 스프레드시트 생성 실패: {e}")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "test":
            test_keyword_manager()
        elif command == "setup":
            setup_keyword_manager()
        elif command == "create":
            create_sample_spreadsheet()
        elif command == "help":
            print("Google Sheets 키워드 매니저 v2.0")
            print("=" * 50)
            print("사용법:")
            print("  python keyword_manager.py test     # 연결 테스트")
            print("  python keyword_manager.py setup    # 설정 가이드")
            print("  python keyword_manager.py create   # 샘플 시트 생성")
            print("  python keyword_manager.py help     # 도움말")
            print("\n💡 기능:")
            print("  • Google Sheets 기반 동적 키워드 관리")
            print("  • 실시간 키워드 업데이트")
            print("  • 카테고리별 키워드 분류")
            print("  • 사용 통계 추적")
            print("  • 캐시를 통한 성능 최적화")
            print("  • 뉴스 수집기와 완전 통합")
        else:
            print(f"❌ 알 수 없는 명령어: {command}")
            print("도움말: python keyword_manager.py help")
    else:
        test_keyword_manager()