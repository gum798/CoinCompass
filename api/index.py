#!/usr/bin/env python3
"""
CoinCompass Vercel Deployment Entry Point
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 환경 변수 설정
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('PYTHONPATH', str(project_root))

# Flask 애플리케이션 임포트
from coincompass.web.app import app, socketio

# Vercel에서는 socketio 대신 일반 Flask app 사용
# WebSocket 기능은 제한적이므로 폴백 처리
if __name__ == "__main__":
    # 로컬 개발 환경
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)
else:
    # Vercel 배포 환경
    # SocketIO 없이 일반 Flask 앱으로 실행
    pass

# Vercel에서 사용할 WSGI 애플리케이션
handler = app