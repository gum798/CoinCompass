import time
import json
from datetime import datetime
from crypto_data import CoinGeckoAPI
from technical_indicators import analyze_coin, TechnicalIndicators, TradingSignals
import pandas as pd

class RealTimeMonitor:
    def __init__(self, config_file="monitor_config.json"):
        self.api = CoinGeckoAPI()
        self.config = self.load_config(config_file)
        self.alerts_log = []
        
    def load_config(self, config_file):
        """모니터링 설정 로드"""
        default_config = {
            "coins": ["bitcoin", "ethereum", "ripple"],
            "interval": 300,  # 5분마다 체크
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "price_change_threshold": 5.0,  # 5% 변동시 알림
            "enable_alerts": True,
            "log_file": "trading_log.txt"
        }
        
        try:
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except FileNotFoundError:
            # 설정 파일이 없으면 기본 설정으로 생성
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"기본 설정 파일 {config_file}을 생성했습니다.")
        
        return default_config
    
    def log_message(self, message):
        """메시지 로그 저장"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        print(log_entry)
        
        # 파일에 로그 저장
        with open(self.config["log_file"], 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def check_price_alerts(self, coin, current_price, previous_price):
        """가격 변동 알림 체크"""
        if previous_price is None:
            return []
        
        price_change = ((current_price - previous_price) / previous_price) * 100
        alerts = []
        
        if abs(price_change) >= self.config["price_change_threshold"]:
            direction = "상승" if price_change > 0 else "하락"
            alert = f"🚨 {coin.upper()} 급격한 가격 {direction}: {price_change:.2f}% (${current_price:,.2f})"
            alerts.append(alert)
        
        return alerts
    
    def check_technical_alerts(self, coin, analysis):
        """기술적 지표 알림 체크"""
        if analysis.empty:
            return []
        
        latest = analysis.iloc[-1]
        alerts = []
        
        # RSI 알림
        if latest['rsi'] <= self.config["rsi_oversold"]:
            alert = f"📈 {coin.upper()} RSI 과매도 신호: {latest['rsi']:.2f} (매수 기회)"
            alerts.append(alert)
        elif latest['rsi'] >= self.config["rsi_overbought"]:
            alert = f"📉 {coin.upper()} RSI 과매수 신호: {latest['rsi']:.2f} (매도 고려)"
            alerts.append(alert)
        
        # 이동평균 교차 알림
        if latest['ma_signal'] == 'BUY':
            alert = f"🔥 {coin.upper()} 골든크로스 발생! (매수 신호)"
            alerts.append(alert)
        elif latest['ma_signal'] == 'SELL':
            alert = f"❄️ {coin.upper()} 데드크로스 발생! (매도 신호)"
            alerts.append(alert)
        
        # 볼린저 밴드 이탈 알림
        if latest['price'] > latest['bb_upper']:
            alert = f"⚡ {coin.upper()} 볼린저 상단 돌파: ${latest['price']:,.2f}"
            alerts.append(alert)
        elif latest['price'] < latest['bb_lower']:
            alert = f"💎 {coin.upper()} 볼린저 하단 터치: ${latest['price']:,.2f}"
            alerts.append(alert)
        
        return alerts
    
    def monitor_coin(self, coin, previous_prices=None):
        """개별 코인 모니터링"""
        try:
            # 현재 가격 조회
            price_data = self.api.get_price(coin)
            if not price_data:
                return None, None
            
            current_price = price_data[coin]['usd']
            
            # 과거 데이터로 기술적 분석
            historical_data = self.api.get_historical_data(coin, days=30)
            if historical_data is None:
                return current_price, []
            
            # 현재 가격을 과거 데이터에 추가
            current_time = pd.Timestamp.now().floor('D')
            if current_time not in historical_data.index:
                historical_data.loc[current_time] = current_price
            
            analysis = analyze_coin(historical_data, coin)
            
            alerts = []
            
            # 가격 변동 알림
            previous_price = previous_prices.get(coin) if previous_prices else None
            price_alerts = self.check_price_alerts(coin, current_price, previous_price)
            alerts.extend(price_alerts)
            
            # 기술적 지표 알림
            technical_alerts = self.check_technical_alerts(coin, analysis)
            alerts.extend(technical_alerts)
            
            return current_price, alerts
            
        except Exception as e:
            error_msg = f"❌ {coin} 모니터링 오류: {str(e)}"
            return None, [error_msg]
    
    def start_monitoring(self):
        """실시간 모니터링 시작"""
        self.log_message("🤖 실시간 코인 모니터링을 시작합니다...")
        self.log_message(f"모니터링 코인: {', '.join(self.config['coins'])}")
        self.log_message(f"체크 간격: {self.config['interval']}초")
        
        previous_prices = {}
        
        try:
            while True:
                self.log_message("\n" + "="*50)
                self.log_message("📊 코인 상태 체크 중...")
                
                for coin in self.config["coins"]:
                    current_price, alerts = self.monitor_coin(coin, previous_prices)
                    
                    if current_price:
                        previous_prices[coin] = current_price
                        
                        # 기본 정보 로그
                        price_change = ""
                        if coin in previous_prices:
                            prev = previous_prices.get(coin + "_prev", current_price)
                            change = ((current_price - prev) / prev) * 100
                            price_change = f" ({change:+.2f}%)"
                        
                        self.log_message(f"💰 {coin.upper()}: ${current_price:,.2f}{price_change}")
                        
                        # 알림 처리
                        if self.config["enable_alerts"] and alerts:
                            for alert in alerts:
                                self.log_message(alert)
                                self.alerts_log.append({
                                    'timestamp': datetime.now(),
                                    'coin': coin,
                                    'alert': alert
                                })
                        
                        # 이전 가격 저장 (변동률 계산용)
                        previous_prices[coin + "_prev"] = current_price
                
                self.log_message(f"⏰ {self.config['interval']}초 후 다시 체크...")
                time.sleep(self.config["interval"])
                
        except KeyboardInterrupt:
            self.log_message("\n🛑 모니터링이 중단되었습니다.")
            self.log_message(f"총 {len(self.alerts_log)}개의 알림이 발생했습니다.")

def main():
    """메인 실행 함수"""
    print("🚀 실시간 코인 모니터링 시스템")
    print("Ctrl+C로 중단할 수 있습니다.")
    
    monitor = RealTimeMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main()