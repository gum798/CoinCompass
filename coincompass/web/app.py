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
from coincompass.simulation.trading_engine import TradingEngine
from coincompass.simulation.portfolio_manager import PortfolioManager
from coincompass.utils.logger import get_logger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'coincompass_secret_key_2025'

# Vercel 환경에서는 SocketIO 비활성화
if os.environ.get('VERCEL_ENV'):
    socketio = None
    print("Vercel 환경에서 실행 중 - SocketIO 비활성화")
else:
    socketio = SocketIO(app, cors_allowed_origins="*")

logger = get_logger(__name__)

# 글로벌 변수
api_provider = MultiAPIProvider()
market_analyzer = MarketAnalyzer()
price_analyzer = PriceDriverAnalyzer()
technical_analyzer = TechnicalAnalyzer()
macro_analyzer = MacroeconomicAnalyzer()
api_key_manager = get_api_key_manager()
trading_engine = TradingEngine()
portfolio_manager = PortfolioManager()

# 실시간 데이터 캐시
live_data = {
    'prices': {},
    'last_update': None,
    'market_analysis': {},
    'macro_data': {}
}

# 모니터링 설정 (환경변수 기반)
monitor_settings = {
    'enabled': os.getenv('MONITORING_ENABLED', 'true').lower() == 'true',
    'interval': int(os.getenv('MONITORING_INTERVAL', '1800')),  # 기본 30분 (1800초)
    'initial_delay': int(os.getenv('MONITORING_INITIAL_DELAY', '60')),  # 시작 후 1분 대기
    'api_call_enabled': os.getenv('API_CALLS_ENABLED', 'true').lower() == 'true',
    'api_call_interval': int(os.getenv('API_CALL_INTERVAL', '1800')),  # API 호출 간격 (30분)
    'coins': os.getenv('MONITORING_COINS', 'bitcoin,ethereum,ripple,cardano,solana').split(','),
    'alerts': {
        'price_change_threshold': float(os.getenv('PRICE_ALERT_THRESHOLD', '5.0')),
        'volume_change_threshold': float(os.getenv('VOLUME_ALERT_THRESHOLD', '50.0'))
    }
}

class RealTimeMonitor:
    """실시간 모니터링 클래스"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.first_run = True
        self.last_api_call = None
    
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
        # 초기 지연 시간 적용
        if self.first_run and monitor_settings.get('initial_delay', 0) > 0:
            logger.info(f"초기 지연 {monitor_settings['initial_delay']}초 대기 중...")
            time.sleep(monitor_settings['initial_delay'])
        
        while self.running:
            try:
                now = datetime.now()
                should_call_api = self._should_call_api(now)
                
                if should_call_api:
                    logger.info("API 호출 실행 중...")
                    
                    # 가격 데이터 수집 (API 호출)
                    if monitor_settings.get('api_call_enabled', True):
                        self._update_price_data()
                        self._update_market_analysis()
                        self._update_macro_data()
                        self.last_api_call = now
                        logger.info(f"API 호출 완료. 다음 호출: {monitor_settings['api_call_interval']}초 후")
                    else:
                        logger.info("API 호출이 비활성화되어 있습니다.")
                else:
                    # API 호출 없이 기존 데이터로 작업
                    logger.debug("기존 데이터 사용 중...")
                
                live_data['last_update'] = now
                
                # WebSocket으로 데이터 전송 (Vercel에서는 건너뛰기)
                if socketio:
                    socketio.emit('data_update', {
                        'prices': live_data['prices'],
                        'market_analysis': live_data['market_analysis'],
                        'macro_data': live_data['macro_data'],
                        'timestamp': live_data['last_update'].isoformat(),
                        'api_call_made': should_call_api
                    })
                
                # 알림 체크 (기존 데이터 기반)
                if live_data['prices']:
                    self._check_alerts()
                
                self.first_run = False
                
            except Exception as e:
                logger.error(f"모니터링 오류: {str(e)}")
            
            # 다음 체크까지 대기
            sleep_time = monitor_settings['interval']
            logger.debug(f"다음 체크까지 {sleep_time}초 대기...")
            time.sleep(sleep_time)
    
    def _should_call_api(self, now):
        """API 호출 여부 판단"""
        if not monitor_settings.get('api_call_enabled', True):
            return False
            
        # 첫 실행이거나 마지막 API 호출이 없는 경우
        if self.first_run or self.last_api_call is None:
            return True
            
        # 마지막 API 호출 이후 충분한 시간이 경과했는지 확인
        time_since_last_call = (now - self.last_api_call).total_seconds()
        return time_since_last_call >= monitor_settings['api_call_interval']
    
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
                # 안전한 값 추출 함수
                def safe_extract_value(data, default='N/A'):
                    """안전하게 숫자 값을 추출"""
                    if isinstance(data, (int, float)):
                        return data
                    elif isinstance(data, dict) and 'value' in data:
                        return data['value']
                    elif isinstance(data, dict) and 'price' in data:
                        return data['price']
                    else:
                        return default
                
                # 데이터 추출
                fed_rate_data = indicators.get('fed_rate', 'N/A')
                unemployment_data = indicators.get('unemployment', 'N/A')
                
                market_indices = indicators.get('market_indices', {})
                vix_data = market_indices.get('VIX', 'N/A')
                sp500_data = market_indices.get('SP500', 'N/A')
                
                live_data['macro_data'] = {
                    'fed_rate': safe_extract_value(fed_rate_data),
                    'unemployment': safe_extract_value(unemployment_data),
                    'vix': safe_extract_value(vix_data),
                    'sp500': safe_extract_value(sp500_data),
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
                    
                    if socketio:
                        socketio.emit('alert', alert)
                    logger.info(f"알림 발송: {alert['message']}")
        except Exception as e:
            logger.error(f"알림 체크 오류: {str(e)}")

# 실시간 모니터 인스턴스
real_time_monitor = RealTimeMonitor()

@app.route('/')
def index():
    """메인 대시보드 페이지"""
    # EmailJS 설정 (환경변수에서 읽기)
    emailjs_config = {
        'service_id': os.getenv('EMAILJS_SERVICE_ID', ''),
        'template_id': os.getenv('EMAILJS_TEMPLATE_ID', 'template_feedback'),
        'public_key': os.getenv('EMAILJS_PUBLIC_KEY', '')
    }
    
    return render_template('dashboard.html',
                         coins=monitor_settings['coins'],
                         settings=monitor_settings,
                         emailjs=emailjs_config)

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

@app.route('/api/historical-prices')
def api_historical_prices():
    """시간대별 과거 가격 데이터 API"""
    coins = request.args.get('coins', 'bitcoin,ethereum,ripple').split(',')
    period = request.args.get('period', '1d')  # 1h, 1d, 1w, 1m, 3m, 1y, all
    
    # 기간별 일수 매핑
    period_days = {
        '1h': 1/24,      # 1시간
        '1d': 1,         # 1일
        '1w': 7,         # 1주
        '1m': 30,        # 1개월
        '3m': 90,        # 3개월
        '1y': 365,       # 1년
        'all': 365 * 2   # 2년
    }
    
    days = period_days.get(period, 1)
    
    historical_data = {}
    for coin in coins:
        try:
            # yfinance를 사용해서 과거 데이터 가져오기
            import yfinance as yf
            
            # 코인 심볼 매핑
            coin_symbols = {
                'bitcoin': 'BTC-USD',
                'ethereum': 'ETH-USD',
                'ripple': 'XRP-USD',
                'cardano': 'ADA-USD',
                'solana': 'SOL-USD'
            }
            
            symbol = coin_symbols.get(coin.strip(), f"{coin.upper()}-USD")
            ticker = yf.Ticker(symbol)
            
            # 기간별 인터벌 설정 (yfinance 제한 고려)
            if period == '1h':
                # 1시간: 최근 1일간 2분 간격으로 시도
                try:
                    hist = ticker.history(period="1d", interval="2m")
                    if not hist.empty:
                        # 최근 1시간 분량만 추출 (30개 데이터 포인트, 2분 * 30 = 60분)
                        hist = hist.tail(30)
                    else:
                        # 실패시 5분 간격으로 시도
                        hist = ticker.history(period="1d", interval="5m")
                        if not hist.empty:
                            hist = hist.tail(12)
                except:
                    # 마지막 대안: 1일 데이터에서 시간별로 샘플링
                    hist = ticker.history(period="2d", interval="1h")
                    if not hist.empty:
                        hist = hist.tail(24)
                        
            elif period == '1d':
                # 1일: 여러 방법 시도
                try:
                    # 방법 1: 5일간 30분 간격
                    hist = ticker.history(period="5d", interval="30m")
                    if not hist.empty:
                        # 최근 1일 분량만 추출 (48개 데이터 포인트, 30분 * 48 = 24시간)
                        hist = hist.tail(48)
                    else:
                        # 방법 2: 2일간 1시간 간격
                        hist = ticker.history(period="2d", interval="1h")
                        if not hist.empty:
                            hist = hist.tail(24)
                except:
                    # 마지막 대안: 5일간 1시간 간격
                    hist = ticker.history(period="5d", interval="1h")
                    if not hist.empty:
                        hist = hist.tail(24)
            elif period == '1w':
                # 1주: 1개월간 1시간 간격
                hist = ticker.history(period="1mo", interval="1h")
                if not hist.empty:
                    # 최근 1주 분량만 추출 (168시간)
                    hist = hist.tail(168)
            elif period == '1m':
                # 1개월: 3개월간 1일 간격
                hist = ticker.history(period="3mo", interval="1d")
                if not hist.empty:
                    # 최근 1개월 분량만 추출 (30일)
                    hist = hist.tail(30)
            elif period == '3m':
                # 3개월: 1년간 1일 간격
                hist = ticker.history(period="1y", interval="1d")
                if not hist.empty:
                    # 최근 3개월 분량만 추출 (90일)
                    hist = hist.tail(90)
            elif period == '1y':
                # 1년: 2년간 1주 간격
                hist = ticker.history(period="2y", interval="1wk")
                if not hist.empty:
                    # 최근 1년 분량만 추출 (52주)
                    hist = hist.tail(52)
            else:  # 'all'
                # 전체: 최대 5년간 1개월 간격
                hist = ticker.history(period="5y", interval="1mo")
            
            if not hist.empty:
                # 기준 가격 (첫 번째 가격)
                base_price = hist['Close'].iloc[0]
                
                # 데이터 포인트 준비
                timestamps = []
                prices = []
                percent_changes = []
                
                for idx, row in hist.iterrows():
                    timestamps.append(idx.strftime('%Y-%m-%d %H:%M:%S'))
                    prices.append(float(row['Close']))
                    percent_change = ((row['Close'] - base_price) / base_price) * 100
                    percent_changes.append(float(percent_change))
                
                historical_data[coin] = {
                    'timestamps': timestamps,
                    'prices': prices,
                    'percent_changes': percent_changes,
                    'base_price': float(base_price),
                    'current_price': float(hist['Close'].iloc[-1]),
                    'data_points': len(timestamps),
                    'period_requested': period,
                    'symbol_used': symbol
                }
                
                logger.info(f"{coin} ({symbol}) {period} 데이터 성공: {len(timestamps)}개 포인트")
            else:
                logger.warning(f"{coin} ({symbol}) {period} 데이터 없음")
                historical_data[coin] = {
                    'error': 'No data available',
                    'symbol': symbol,
                    'period': period,
                    'message': f'yfinance에서 {symbol}의 {period} 데이터를 가져올 수 없습니다'
                }
                
        except Exception as e:
            logger.error(f"{coin} 과거 데이터 조회 오류 (period={period}): {str(e)}")
            # 오류 정보를 클라이언트에 전달
            historical_data[coin] = {
                'error': str(e),
                'symbol': symbol if 'symbol' in locals() else 'unknown',
                'period': period
            }
    
    return jsonify({
        'period': period,
        'data': historical_data,
        'timestamp': datetime.now().isoformat()
    })

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
    
    # EmailJS 설정
    emailjs_config = {
        'service_id': os.getenv('EMAILJS_SERVICE_ID', ''),
        'template_id': os.getenv('EMAILJS_TEMPLATE_ID', 'template_feedback'),
        'public_key': os.getenv('EMAILJS_PUBLIC_KEY', '')
    }
    
    return render_template('settings.html',
                         settings=monitor_settings,
                         fred_key_exists=fred_key_exists,
                         emailjs=emailjs_config)

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

# 모의투자 관련 라우트
@app.route('/simulation')
def simulation():
    """모의투자 페이지"""
    user_id = 'default'  # 추후 사용자 인증 시스템 추가
    
    # 포트폴리오가 없으면 생성
    portfolio = portfolio_manager.get_portfolio(user_id)
    if not portfolio:
        portfolio = portfolio_manager.create_portfolio(user_id)
    
    # 현재 가격으로 포트폴리오 업데이트
    trading_engine.update_portfolio_prices(user_id)
    
    # EmailJS 설정
    emailjs_config = {
        'service_id': os.getenv('EMAILJS_SERVICE_ID', ''),
        'template_id': os.getenv('EMAILJS_TEMPLATE_ID', 'template_feedback'),
        'public_key': os.getenv('EMAILJS_PUBLIC_KEY', '')
    }
    
    return render_template('simulation.html',
                         coins=monitor_settings['coins'],
                         emailjs=emailjs_config)

@app.route('/api/simulation/portfolio')
def api_simulation_portfolio():
    """포트폴리오 조회 API"""
    user_id = 'default'
    
    try:
        # 포트폴리오가 없으면 생성
        portfolio = portfolio_manager.get_portfolio(user_id)
        if not portfolio:
            portfolio = portfolio_manager.create_portfolio(user_id)
        
        # 현재 가격으로 업데이트
        trading_engine.update_portfolio_prices(user_id)
        
        # 거래 요약 정보
        summary = trading_engine.get_trading_summary(user_id)
        
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"포트폴리오 조회 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulation/buy', methods=['POST'])
def api_simulation_buy():
    """매수 주문 API"""
    user_id = 'default'
    
    try:
        data = request.get_json()
        coin_id = data.get('coin_id')
        amount = float(data.get('amount', 0))  # 달러 금액
        
        if not coin_id or amount <= 0:
            return jsonify({'error': '유효하지 않은 주문 정보입니다'}), 400
        
        # 현재 가격 조회
        current_price = trading_engine.get_current_price(coin_id)
        if not current_price:
            return jsonify({'error': f'{coin_id} 가격 정보를 가져올 수 없습니다'}), 400
        
        # 수량 계산
        quantity = amount / current_price
        
        # 매수 주문 실행
        success, message, order = trading_engine.create_buy_order(user_id, coin_id, quantity)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'order': trading_engine.order_to_dict(order) if order else None
            })
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        logger.error(f"매수 주문 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulation/sell', methods=['POST'])
def api_simulation_sell():
    """매도 주문 API"""
    user_id = 'default'
    
    try:
        data = request.get_json()
        coin_id = data.get('coin_id')
        percentage = float(data.get('percentage', 0))  # 매도할 비율 (0-100)
        
        if not coin_id or percentage <= 0 or percentage > 100:
            return jsonify({'error': '유효하지 않은 주문 정보입니다'}), 400
        
        # 포트폴리오 확인
        portfolio = portfolio_manager.get_portfolio(user_id)
        if not portfolio or coin_id not in portfolio.positions:
            return jsonify({'error': f'{coin_id}를 보유하고 있지 않습니다'}), 400
        
        # 매도 수량 계산
        position = portfolio.positions[coin_id]
        quantity = position.quantity * (percentage / 100)
        
        # 매도 주문 실행
        success, message, order = trading_engine.create_sell_order(user_id, coin_id, quantity)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'order': trading_engine.order_to_dict(order) if order else None
            })
        else:
            return jsonify({'success': False, 'error': message}), 400
            
    except Exception as e:
        logger.error(f"매도 주문 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulation/orders')
def api_simulation_orders():
    """주문 내역 조회 API"""
    user_id = 'default'
    
    try:
        orders = trading_engine.get_user_orders(user_id, limit=20)
        orders_data = [trading_engine.order_to_dict(order) for order in orders]
        
        return jsonify({'orders': orders_data})
        
    except Exception as e:
        logger.error(f"주문 내역 조회 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulation/reset', methods=['POST'])
def api_simulation_reset():
    """포트폴리오 리셋 API"""
    user_id = 'default'
    
    try:
        portfolio_manager.reset_portfolio(user_id)
        return jsonify({'success': True, 'message': '포트폴리오가 리셋되었습니다'})
        
    except Exception as e:
        logger.error(f"포트폴리오 리셋 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500

# WebSocket 이벤트 핸들러 (SocketIO가 있을 때만 등록)
if socketio:
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
    
    # 포트 설정 (Railway, Heroku 등 클라우드 환경 지원)
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"📱 웹 브라우저에서 http://{host}:{port} 접속")
    print("🔄 실시간 업데이트 지원")
    print(f"⚙️ 설정: http://{host}:{port}/settings")
    print("🛑 종료: Ctrl+C")
    print("="*50)
    
    # 모니터링이 활성화되어 있으면 자동 시작
    if monitor_settings['enabled']:
        real_time_monitor.start()
        print("🟢 실시간 모니터링 자동 시작됨")
        print(f"📊 모니터링 대상: {', '.join(monitor_settings['coins'])}")
    
    # 개발 모드에서 실행
    if socketio:
        socketio.run(app, debug=debug, host=host, port=port, allow_unsafe_werkzeug=True)
    else:
        app.run(debug=debug, host=host, port=port)