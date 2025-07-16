"""
실시간 모니터링 시스템
기존 real_time_monitor.py를 개선하여 재구조화
"""

import time
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..core.data_manager import DataManager
from ..core.models import AnalysisResult, PriceData
from ..api.multi_provider import MultiAPIProvider
from ..analysis.technical import TechnicalAnalyzer
from ..config.settings import Settings
from ..utils.logger import get_logger
from .alerts import AlertManager

logger = get_logger(__name__)

class RealTimeMonitor:
    """실시간 모니터링 시스템"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.settings = Settings(config_path)
        self.data_manager = DataManager()
        self.api_provider = MultiAPIProvider()
        self.technical_analyzer = TechnicalAnalyzer()
        self.alert_manager = AlertManager(self.settings)
        
        self.is_running = False
        self.monitoring_results = {}
        
        logger.info("RealTimeMonitor 초기화 완료")
    
    def analyze_coin(self, coin_id: str) -> Optional[AnalysisResult]:
        """개별 코인 분석"""
        try:
            # 현재 가격 데이터 조회
            price_data = self.api_provider.get_price_data(coin_id)
            if not price_data:
                logger.warning(f"{coin_id} 가격 데이터 조회 실패")
                return None
            
            # 과거 데이터 조회 (캐시 활용)
            cache_key = f"historical_{coin_id}"
            historical_data = self.data_manager.get_cached_data(cache_key)
            
            if not historical_data:
                # TODO: 과거 데이터 조회 API 구현 필요
                logger.info(f"{coin_id} 과거 데이터 캐시 없음")
                # 임시로 현재 가격만으로 분석
                price_series = pd.Series([price_data.price])
            else:
                price_series = pd.Series(historical_data)
            
            # 기술적 분석 수행
            technical_indicators = self.technical_analyzer.analyze_price_data(price_series)
            trading_signal = self.technical_analyzer.generate_trading_signal(price_series, technical_indicators)
            
            # 분석 결과 생성
            analysis_result = AnalysisResult(
                coin_id=coin_id,
                price_data=price_data,
                technical_indicators=technical_indicators,
                trading_signal=trading_signal
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"{coin_id} 분석 중 오류: {str(e)}")
            return None
    
    def monitor_single_cycle(self) -> Dict[str, AnalysisResult]:
        """단일 모니터링 사이클 실행"""
        results = {}
        
        logger.info("🔄 모니터링 사이클 시작")
        
        for coin_id in self.settings.get_coins_list():
            logger.debug(f"📊 {coin_id} 분석 중...")
            
            analysis_result = self.analyze_coin(coin_id)
            if analysis_result:
                results[coin_id] = analysis_result
                
                # 알림 체크
                self.alert_manager.check_alerts(analysis_result)
                
                # 결과 로깅
                price = analysis_result.price_data.price
                signal = analysis_result.trading_signal.signal
                confidence = analysis_result.trading_signal.confidence
                
                logger.info(f"  💰 {coin_id}: ${price:,.2f} | {signal} ({confidence:.1%})")
            
            # API 제한 방지
            time.sleep(1)
        
        logger.info(f"✅ 모니터링 사이클 완료: {len(results)}개 코인 분석")
        return results
    
    def start_monitoring(self):
        """모니터링 시작"""
        if self.is_running:
            logger.warning("모니터링이 이미 실행 중입니다")
            return
        
        self.is_running = True
        interval = self.settings.monitoring.interval_seconds
        
        logger.info(f"🚀 실시간 모니터링 시작 (간격: {interval}초)")
        logger.info(f"📋 대상 코인: {', '.join(self.settings.get_coins_list())}")
        
        try:
            while self.is_running:
                cycle_start = datetime.now()
                
                # 모니터링 실행
                results = self.monitor_single_cycle()
                self.monitoring_results = results
                
                # 결과 저장
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.data_manager.save_to_file(
                    {coin_id: result.to_dict() for coin_id, result in results.items()},
                    f"monitoring_results_{timestamp}.json",
                    "data/logs"
                )
                
                # 다음 실행까지 대기
                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                sleep_time = max(0, interval - cycle_duration)
                
                if sleep_time > 0:
                    logger.info(f"⏰ {sleep_time:.1f}초 후 다음 사이클...")
                    time.sleep(sleep_time)
                else:
                    logger.warning(f"⚠️ 모니터링 사이클이 설정 간격({interval}초)보다 오래 걸렸습니다 ({cycle_duration:.1f}초)")
                    
        except KeyboardInterrupt:
            logger.info("🛑 사용자에 의해 모니터링이 중단되었습니다")
        except Exception as e:
            logger.error(f"❌ 모니터링 중 오류 발생: {str(e)}")
        finally:
            self.is_running = False
            logger.info("📊 모니터링 종료")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        if self.is_running:
            self.is_running = False
            logger.info("🛑 모니터링 중지 요청")
        else:
            logger.info("모니터링이 실행 중이 아닙니다")
    
    def get_latest_results(self) -> Dict[str, AnalysisResult]:
        """최신 분석 결과 조회"""
        return self.monitoring_results.copy()
    
    def get_monitoring_stats(self) -> Dict:
        """모니터링 통계 조회"""
        return {
            'is_running': self.is_running,
            'monitored_coins': len(self.settings.get_coins_list()),
            'last_update': max([r.analysis_timestamp for r in self.monitoring_results.values()]) if self.monitoring_results else None,
            'api_stats': self.api_provider.get_stats(),
            'alert_stats': self.alert_manager.get_stats()
        }