# Python 3.9 베이스 이미지 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# pip 업그레이드
RUN pip install --upgrade pip setuptools wheel

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치 (더 안정적인 방법)
RUN pip install --no-cache-dir --timeout 1000 -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 설정
EXPOSE 5001

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV FLASK_ENV=production

# 데이터 디렉토리 생성
RUN mkdir -p data/simulation

# 애플리케이션 실행
CMD ["python", "main.py"]