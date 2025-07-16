#!/usr/bin/env python3
"""
CoinCompass Main Entry Point
Railway 배포를 위한 단순화된 진입점
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 환경 변수 설정
os.environ.setdefault('PYTHONPATH', str(project_root))

def create_minimal_app():
    """의존성 오류 시 최소한의 Flask 앱 생성"""
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return jsonify({
            "status": "CoinCompass Server Running",
            "message": "일부 기능이 제한될 수 있습니다. 필요한 패키지를 설치해주세요.",
            "missing_dependencies": "pandas, yfinance 등"
        })
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy"})
    
    return app

try:
    # CoinCompass 웹 애플리케이션 임포트 및 실행
    from coincompass.web.app import app, socketio
    
    if __name__ == "__main__":
        # 포트 설정 (Railway, Heroku 등 클라우드 환경 지원)
        port = int(os.environ.get('PORT', 5001))
        host = os.environ.get('HOST', '0.0.0.0')
        debug = os.environ.get('FLASK_ENV', 'production') != 'production'
        
        print("🚂 CoinCompass Railway 배포 시작")
        print(f"📱 포트: {port}")
        print(f"🌐 호스트: {host}")
        print(f"🔧 디버그 모드: {debug}")
        
        # 실행
        if socketio and hasattr(socketio, 'run'):
            socketio.run(app, debug=debug, host=host, port=port)
        else:
            app.run(debug=debug, host=host, port=port)
            
except ImportError as e:
    print(f"❌ 모듈 임포트 오류: {e}")
    print("최소한의 Flask 서버를 시작합니다...")
    
    # 최소한의 Flask 앱으로 폴백
    app = create_minimal_app()
    
    if __name__ == "__main__":
        port = int(os.environ.get('PORT', 5001))
        host = os.environ.get('HOST', '0.0.0.0')
        app.run(debug=False, host=host, port=port)
        
except Exception as e:
    print(f"❌ 애플리케이션 시작 오류: {e}")
    print("최소한의 서버를 시작합니다...")
    
    # 최소한의 Flask 앱으로 폴백
    app = create_minimal_app()
    
    if __name__ == "__main__":
        port = int(os.environ.get('PORT', 5001))
        host = os.environ.get('HOST', '0.0.0.0')
        app.run(debug=False, host=host, port=port)