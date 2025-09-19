#!/bin/bash
# Google News AI Agent 실행 스크립트

set -e

echo "🤖 Google News AI Agent 시작"
echo "==============================="

# 가상환경 활성화 (존재하는 경우)
if [ -d "venv" ]; then
    echo "📦 가상환경 활성화..."
    source venv/bin/activate
fi

# Python 경로 확인
echo "🐍 Python 버전: $(python3 --version)"

# 필요한 패키지 설치 확인
echo "📋 패키지 의존성 확인..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --quiet
    echo "✅ 패키지 설치 완료"
fi

# 환경변수 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다. 환경변수를 직접 설정해주세요."
fi

# Google Sheets 인증 파일 확인
if [ ! -f "credentials.json" ] && [ ! -f "credential.json" ]; then
    echo "⚠️  Google Sheets 인증 파일이 없습니다."
    echo "💡 credentials.json 또는 credential.json 파일을 추가해주세요."
fi

# 로그 디렉토리 생성
mkdir -p logs

echo ""
echo "🚀 시스템 시작 중..."
echo "💡 실행 옵션:"
echo "   ./run.sh            - 메인 뉴스 수집 실행"
echo "   ./run.sh test        - 시스템 테스트"
echo "   ./run.sh schedule    - 스케줄러 시작"
echo "   ./run.sh status      - 상태 확인"
echo ""

# 명령행 인자에 따라 실행
if [ $# -eq 0 ]; then
    # 기본 실행
    python3 main.py
elif [ "$1" = "test" ]; then
    # 테스트 실행
    python3 main.py test
elif [ "$1" = "schedule" ]; then
    # 스케줄러 실행
    python3 main.py schedule
elif [ "$1" = "status" ]; then
    # 상태 확인
    python3 main.py status
elif [ "$1" = "config" ]; then
    # 설정 확인
    python3 main.py config
elif [ "$1" = "keyword-test" ]; then
    # 키워드 매니저 테스트
    python3 keyword_manager.py test
else
    echo "❌ 알 수 없는 명령어: $1"
    echo "사용법: ./run.sh [test|schedule|status|config|keyword-test]"
    exit 1
fi