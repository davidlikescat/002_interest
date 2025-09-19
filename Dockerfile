# Google News AI Agent Dockerfile
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY *.py ./
COPY run.sh ./
RUN chmod +x run.sh

# 로그 디렉토리 생성
RUN mkdir -p logs

# 환경변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python3 -c "from config import Config; Config.validate_config()" || exit 1

# 기본 포트 (필요시)
EXPOSE 8000

# 기본 실행 명령
CMD ["python3", "main.py", "schedule"]