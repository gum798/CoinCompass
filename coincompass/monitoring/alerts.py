"""
알림 관리 시스템
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

from ..core.models import AnalysisResult, PriceData
from ..config.settings import Settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class Alert:
    """알림 데이터 클래스"""
    coin_id: str
    alert_type: str
    message: str
    timestamp: datetime
    data: Dict = None

class AlertManager:
    """알림 관리자"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.alert_history = []
        self.last_alerts = {}  # 중복 알림 방지용
        self.alert_callbacks = []
        
        logger.info("AlertManager 초기화 완료")
    
    def add_callback(self, callback: Callable[[Alert], None]):
        """알림 콜백 함수 추가"""
        self.alert_callbacks.append(callback)
    
    def send_alert(self, alert: Alert):
        """알림 발송"""
        self.alert_history.append(alert)
        
        # 로그 출력
        logger.info(f"🚨 알림: {alert.message}")
        
        # 콜백 함수들 실행
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"알림 콜백 실행 오류: {str(e)}")
    
    def check_price_alerts(self, analysis_result: AnalysisResult):
        """가격 변동 알림 체크"""
        coin_id = analysis_result.coin_id
        current_price = analysis_result.price_data.price
        price_change_24h = analysis_result.price_data.price_change_24h
        
        if price_change_24h is None:
            return
        
        threshold = self.settings.monitoring.price_change_threshold
        
        # 급격한 변동 알림
        if abs(price_change_24h) >= threshold:
            # 중복 알림 방지 (1시간 내)
            alert_key = f"price_change_{coin_id}"
            last_alert_time = self.last_alerts.get(alert_key)
            
            if not last_alert_time or (datetime.now() - last_alert_time) > timedelta(hours=1):
                direction = "급등" if price_change_24h > 0 else "급락"
                
                alert = Alert(
                    coin_id=coin_id,
                    alert_type="price_change",
                    message=f"{coin_id.upper()} {direction}: {price_change_24h:+.2f}% (${current_price:,.2f})",
                    timestamp=datetime.now(),
                    data={
                        'price': current_price,
                        'change_24h': price_change_24h,
                        'threshold': threshold
                    }
                )
                
                self.send_alert(alert)
                self.last_alerts[alert_key] = datetime.now()
    
    def check_technical_alerts(self, analysis_result: AnalysisResult):
        """기술적 지표 알림 체크"""
        coin_id = analysis_result.coin_id
        indicators = analysis_result.technical_indicators
        trading_signal = analysis_result.trading_signal
        
        # RSI 과매수/과매도 알림
        if indicators.rsi is not None:
            rsi_oversold = self.settings.monitoring.rsi_oversold
            rsi_overbought = self.settings.monitoring.rsi_overbought
            
            if indicators.rsi <= rsi_oversold:
                alert_key = f"rsi_oversold_{coin_id}"
                if self._should_send_alert(alert_key, hours=2):
                    alert = Alert(
                        coin_id=coin_id,
                        alert_type="rsi_oversold",
                        message=f"{coin_id.upper()} RSI 과매도: {indicators.rsi:.1f} (매수 기회)",
                        timestamp=datetime.now(),
                        data={'rsi': indicators.rsi, 'threshold': rsi_oversold}
                    )
                    self.send_alert(alert)
                    self.last_alerts[alert_key] = datetime.now()
            
            elif indicators.rsi >= rsi_overbought:
                alert_key = f"rsi_overbought_{coin_id}"
                if self._should_send_alert(alert_key, hours=2):
                    alert = Alert(
                        coin_id=coin_id,
                        alert_type="rsi_overbought",
                        message=f"{coin_id.upper()} RSI 과매수: {indicators.rsi:.1f} (매도 고려)",
                        timestamp=datetime.now(),
                        data={'rsi': indicators.rsi, 'threshold': rsi_overbought}
                    )
                    self.send_alert(alert)
                    self.last_alerts[alert_key] = datetime.now()
        
        # 강한 매매 신호 알림
        if trading_signal.confidence >= 0.8:
            alert_key = f"strong_signal_{coin_id}_{trading_signal.signal}"
            if self._should_send_alert(alert_key, hours=1):
                alert = Alert(
                    coin_id=coin_id,
                    alert_type="strong_signal",
                    message=f"{coin_id.upper()} 강한 {trading_signal.signal} 신호: {trading_signal.confidence:.1%} ({trading_signal.reason})",
                    timestamp=datetime.now(),
                    data={
                        'signal': trading_signal.signal,
                        'confidence': trading_signal.confidence,
                        'reason': trading_signal.reason
                    }
                )
                self.send_alert(alert)
                self.last_alerts[alert_key] = datetime.now()
    
    def check_alerts(self, analysis_result: AnalysisResult):
        """전체 알림 체크"""
        if not self.settings.monitoring.enable_alerts:
            return
        
        try:
            self.check_price_alerts(analysis_result)
            self.check_technical_alerts(analysis_result)
        except Exception as e:
            logger.error(f"알림 체크 중 오류: {str(e)}")
    
    def _should_send_alert(self, alert_key: str, hours: int = 1) -> bool:
        """알림 발송 여부 판단 (중복 방지)"""
        last_alert_time = self.last_alerts.get(alert_key)
        if not last_alert_time:
            return True
        
        return (datetime.now() - last_alert_time) > timedelta(hours=hours)
    
    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """최근 알림 조회"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.timestamp > cutoff_time]
    
    def get_stats(self) -> Dict:
        """알림 통계 조회"""
        recent_alerts = self.get_recent_alerts(24)
        
        return {
            'total_alerts': len(self.alert_history),
            'recent_alerts_24h': len(recent_alerts),
            'alert_types': {},
            'enabled': self.settings.monitoring.enable_alerts
        }
    
    def clear_old_alerts(self, days: int = 7):
        """오래된 알림 삭제"""
        cutoff_time = datetime.now() - timedelta(days=days)
        initial_count = len(self.alert_history)
        
        self.alert_history = [alert for alert in self.alert_history if alert.timestamp > cutoff_time]
        
        deleted_count = initial_count - len(self.alert_history)
        if deleted_count > 0:
            logger.info(f"오래된 알림 {deleted_count}개 삭제")

# 기본 알림 콜백 함수들
def console_alert_callback(alert: Alert):
    """콘솔 알림 출력"""
    print(f"[{alert.timestamp.strftime('%H:%M:%S')}] {alert.message}")

def file_alert_callback(alert: Alert, file_path: str = "data/logs/alerts.log"):
    """파일 알림 저장"""
    import os
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"[{alert.timestamp.isoformat()}] {alert.alert_type}: {alert.message}\n")