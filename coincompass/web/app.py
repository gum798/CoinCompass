#!/usr/bin/env python3
"""
CoinCompass Web Dashboard
Flask 기반 실시간 암호화폐 분석 대시보드
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from threading import Thread
import time

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit, disconnect
import pandas as pd

# CoinCompass 모듈 임포트
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from coincompass.api.multi_provider import MultiAPIProvider
from coincompass.analysis.market_analyzer import MarketAnalyzer
from coincompass.analysis.price_driver import PriceDriverAnalyzer
from coincompass.analysis.technical import TechnicalAnalyzer
from coincompass.analysis.macro import MacroeconomicAnalyzer
from coincompass.config.api_keys import get_api_key_manager
from coincompass.utils.logger import get_logger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'coincompass_secret_key_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

logger = get_logger(__name__)

# 글로벌 변수
api_provider = MultiAPIProvider()
market_analyzer = MarketAnalyzer()
price_analyzer = PriceDriverAnalyzer()
technical_analyzer = TechnicalAnalyzer()
macro_analyzer = MacroeconomicAnalyzer()
api_key_manager = get_api_key_manager()

# 실시간 데이터 캐시
live_data = {
    'prices': {},
    'last_update': None,
    'market_analysis': {},
    'macro_data': {}
}

# 모니터링 설정
monitor_settings = {
    'enabled': False,
    'interval': 30,  # seconds
    'coins': ['bitcoin', 'ethereum', 'ripple'],
    'alerts': {
        'price_change_threshold': 5.0,
        'volume_change_threshold': 50.0
    }
}

class RealTimeMonitor:
    """실시간 모니터링 클래스"""
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """모니터링 시작"""
        if not self.running:
            self.running = True
            self.thread = Thread(target=self._monitor_loop)
            self.thread.daemon = True
            self.thread.start()
            logger.info("실시간 모니터링 시작")
    
    def stop(self):
        """모니터링 중지"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("실시간 모니터링 중지")
    
    def _monitor_loop(self):
        """모니터링 루프"""
        while self.running:
            try:
                # 가격 데이터 수집
                self._update_price_data()
                
                # 시장 분석 업데이트
                self._update_market_analysis()
                
                # 거시경제 데이터 업데이트 (5분마다)
                if not live_data['last_update'] or \
                   (datetime.now() - live_data['last_update']).seconds > 300:
                    self._update_macro_data()
                
                live_data['last_update'] = datetime.now()
                
                # WebSocket으로 데이터 전송
                socketio.emit('data_update', {
                    'prices': live_data['prices'],
                    'market_analysis': live_data['market_analysis'],
                    'macro_data': live_data['macro_data'],
                    'timestamp': live_data['last_update'].isoformat()
                })
                
                # 알림 체크
                self._check_alerts()
                
            except Exception as e:
                logger.error(f"모니터링 오류: {str(e)}")
            
            time.sleep(monitor_settings['interval'])
    
    def _update_price_data(self):
        """가격 데이터 업데이트"""
        try:
            for coin in monitor_settings['coins']:
                price_data = api_provider.get_price_data(coin)
                if price_data:
                    live_data['prices'][coin] = {
                        'price': price_data.price,
                        'change_24h': price_data.price_change_24h,
                        'volume_24h': price_data.volume_24h,
                        'market_cap': price_data.market_cap,
                        'last_updated': datetime.now().isoformat()
                    }
        except Exception as e:
            logger.error(f"가격 데이터 업데이트 오류: {str(e)}")
    
    def _update_market_analysis(self):
        """시장 분석 업데이트"""
        try:
            for coin in monitor_settings['coins']:
                if coin in live_data['prices']:
                    # 간단한 기술적 분석
                    price = live_data['prices'][coin]['price']
                    change_24h = live_data['prices'][coin]['change_24h']
                    
                    # RSI 시뮬레이션 (실제로는 과거 데이터 필요)
                    rsi = 50 + (change_24h * 2)  # 간단한 추정
                    rsi = max(0, min(100, rsi))
                    
                    signal = "HOLD"
                    if rsi > 70:
                        signal = "SELL"
                    elif rsi < 30:
                        signal = "BUY"
                    
                    live_data['market_analysis'][coin] = {
                        'rsi': rsi,
                        'signal': signal,
                        'trend': 'UP' if change_24h > 0 else 'DOWN',
                        'strength': abs(change_24h)
                    }
        except Exception as e:
            logger.error(f"시장 분석 업데이트 오류: {str(e)}")
    
    def _update_macro_data(self):
        """거시경제 데이터 업데이트"""
        try:
            indicators = macro_analyzer.get_economic_indicators()
            if indicators:
                live_data['macro_data'] = {
                    'fed_rate': indicators.get('fed_rate', {}).get('value', 'N/A'),
                    'unemployment': indicators.get('unemployment', {}).get('value', 'N/A'),
                    'vix': indicators.get('market_indices', {}).get('VIX', {}).get('price', 'N/A'),
                    'sp500': indicators.get('market_indices', {}).get('SP500', {}).get('price', 'N/A'),
                    'last_updated': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"거시경제 데이터 업데이트 오류: {str(e)}")
    
    def _check_alerts(self):
        """알림 체크"""
        try:
            for coin, data in live_data['prices'].items():
                change_24h = abs(data.get('change_24h', 0))
                
                if change_24h > monitor_settings['alerts']['price_change_threshold']:
                    alert = {
                        'type': 'price_alert',
                        'coin': coin,
                        'message': f"{coin.upper()} 가격이 24시간 동안 {change_24h:.1f}% 변동했습니다",
                        'severity': 'high' if change_24h > 10 else 'medium',
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    socketio.emit('alert', alert)
                    logger.info(f"알림 발송: {alert['message']}")
        except Exception as e:
            logger.error(f"알림 체크 오류: {str(e)}")

# 실시간 모니터 인스턴스
real_time_monitor = RealTimeMonitor()

@app.route('/')
def index():
    """메인 대시보드 페이지"""
    return render_template('dashboard.html',
                         coins=monitor_settings['coins'],
                         settings=monitor_settings)

@app.route('/api/prices')
def api_prices():
    """가격 데이터 API"""
    coins = request.args.get('coins', 'bitcoin,ethereum,ripple').split(',')
    
    prices = {}
    for coin in coins:
        try:
            price_data = api_provider.get_price_data(coin.strip())
            if price_data:
                prices[coin] = {
                    'price': price_data.price,
                    'change_24h': price_data.price_change_24h,
                    'volume_24h': price_data.volume_24h,
                    'market_cap': price_data.market_cap
                }
        except Exception as e:
            logger.error(f"{coin} 가격 조회 오류: {str(e)}")
            prices[coin] = None
    
    return jsonify(prices)

@app.route('/api/analysis/<coin>')
def api_analysis(coin):
    """코인 분석 API"""
    try:
        # 가격 데이터
        price_data = api_provider.get_price_data(coin)
        if not price_data:
            return jsonify({'error': 'Price data not available'}), 404
        
        # 샘플 가격 시리즈 생성 (실제로는 과거 데이터 사용)
        sample_prices = pd.Series([
            price_data.price * (1 + (i-24)*0.01) for i in range(48)
        ])
        
        # 종합 분석
        analysis = market_analyzer.get_comprehensive_analysis(coin, sample_prices)
        
        # 가격 변동 분석
        price_24h_ago = price_data.price / (1 + price_data.price_change_24h/100)
        price_analysis = price_analyzer.analyze_price_movement(
            coin_id=coin,
            current_price=price_data.price,
            price_24h_ago=price_24h_ago,
            price_data=sample_prices
        )
        
        return jsonify({
            'coin': coin,
            'price': price_data.price,
            'change_24h': price_data.price_change_24h,
            'analysis': analysis,
            'price_movement': {
                'type': price_analysis.movement_type,
                'summary': price_analysis.summary,
                'recommendation': price_analysis.recommendation,
                'confidence': price_analysis.confidence
            }
        })
        
    except Exception as e:
        logger.error(f"{coin} 분석 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/macro')
def api_macro():
    """거시경제 데이터 API"""
    try:
        indicators = macro_analyzer.get_economic_indicators()
        return jsonify(indicators)
    except Exception as e:
        logger.error(f"거시경제 데이터 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/settings')
def settings():
    """설정 페이지"""
    # FRED API 키 상태 확인
    fred_key_exists = api_key_manager.has_api_key('fred')
    
    return render_template('settings.html',
                         settings=monitor_settings,
                         fred_key_exists=fred_key_exists)

@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    """설정 API"""
    if request.method == 'GET':
        return jsonify(monitor_settings)
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # 모니터링 설정 업데이트
            if 'interval' in data:
                monitor_settings['interval'] = max(10, int(data['interval']))
            
            if 'coins' in data:
                monitor_settings['coins'] = data['coins']
            
            if 'alerts' in data:
                monitor_settings['alerts'].update(data['alerts'])
            
            if 'enabled' in data:
                monitor_settings['enabled'] = bool(data['enabled'])
                
                if monitor_settings['enabled']:
                    real_time_monitor.start()
                else:
                    real_time_monitor.stop()
            
            return jsonify({'success': True, 'settings': monitor_settings})
            
        except Exception as e:
            logger.error(f"설정 업데이트 오류: {str(e)}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/fred-key', methods=['POST'])
def api_fred_key():
    """FRED API 키 저장"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return jsonify({'error': 'API 키를 입력하세요'}), 400
        
        # API 키 저장
        success = api_key_manager.save_api_key('fred', api_key)
        
        if success:
            return jsonify({'success': True, 'message': 'FRED API 키가 저장되었습니다'})
        else:
            return jsonify({'error': 'API 키 저장에 실패했습니다'}), 500
            
    except Exception as e:
        logger.error(f"FRED API 키 저장 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500

# WebSocket 이벤트 핸들러
@socketio.on('connect')
def handle_connect():
    """클라이언트 연결"""
    logger.info("클라이언트 연결됨")
    
    # 현재 데이터 전송
    emit('data_update', {
        'prices': live_data['prices'],
        'market_analysis': live_data['market_analysis'],
        'macro_data': live_data['macro_data'],
        'timestamp': live_data['last_update'].isoformat() if live_data['last_update'] else None
    })

@socketio.on('disconnect')
def handle_disconnect():
    """클라이언트 연결 해제"""
    logger.info("클라이언트 연결 해제됨")

@socketio.on('start_monitoring')
def handle_start_monitoring():
    """모니터링 시작 요청"""
    try:
        monitor_settings['enabled'] = True
        real_time_monitor.start()
        emit('monitoring_status', {'status': 'started'})
        logger.info("웹에서 모니터링 시작 요청")
    except Exception as e:
        logger.error(f"모니터링 시작 오류: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    """모니터링 중지 요청"""
    try:
        monitor_settings['enabled'] = False
        real_time_monitor.stop()
        emit('monitoring_status', {'status': 'stopped'})
        logger.info("웹에서 모니터링 중지 요청")
    except Exception as e:
        logger.error(f"모니터링 중지 오류: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('request_analysis')
def handle_request_analysis(data):
    """분석 요청"""
    try:
        coin = data.get('coin', 'bitcoin')
        
        # 간단한 분석 수행
        price_data = api_provider.get_price_data(coin)
        if price_data:
            analysis_result = {
                'coin': coin,
                'price': price_data.price,
                'change_24h': price_data.price_change_24h,
                'analysis_time': datetime.now().isoformat()
            }
            
            emit('analysis_result', analysis_result)
        else:
            emit('error', {'message': f'{coin} 데이터를 가져올 수 없습니다'})
            
    except Exception as e:
        logger.error(f"분석 요청 오류: {str(e)}")
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    print("🌐 CoinCompass Web Dashboard 시작")
    print("="*50)
    print("📱 웹 브라우저에서 http://localhost:5001 접속")
    print("🔄 실시간 업데이트 지원")
    print("⚙️ 설정: http://localhost:5001/settings")
    print("🛑 종료: Ctrl+C")
    print("="*50)
    
    # 개발 모드에서 실행
    socketio.run(app, debug=True, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)