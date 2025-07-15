"""
백테스팅 및 검증 모듈
과거 데이터를 사용하여 가격 변동 요인 분석의 정확성을 검증
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import requests
import json

from .price_driver import PriceDriverAnalyzer, PriceMovementAnalysis
from .technical import TechnicalAnalyzer
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class ValidationResult:
    """검증 결과"""
    date: str
    actual_change: float
    predicted_movement: str
    actual_movement: str
    accuracy: bool
    confidence: float
    primary_factors: List[str]
    
@dataclass 
class BacktestReport:
    """백테스트 보고서"""
    period: str
    total_predictions: int
    correct_predictions: int
    accuracy_rate: float
    movement_type_accuracy: Dict[str, float]
    factor_effectiveness: Dict[str, float]
    validation_results: List[ValidationResult]
    summary: str

class HistoricalDataCollector:
    """과거 데이터 수집기"""
    
    def __init__(self):
        self.crypto_symbols = {
            'bitcoin': 'BTC-USD',
            'ethereum': 'ETH-USD', 
            'ripple': 'XRP-USD'
        }
    
    def get_historical_crypto_data(self, coin_id: str, days: int = 30) -> Optional[pd.DataFrame]:
        """암호화폐 과거 데이터 수집"""
        try:
            symbol = self.crypto_symbols.get(coin_id)
            if not symbol:
                logger.error(f"지원하지 않는 코인: {coin_id}")
                return None
            
            # Yahoo Finance에서 데이터 수집
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            hist = ticker.history(start=start_date, end=end_date, interval='1h')
            
            if hist.empty:
                logger.error(f"{coin_id} 데이터 수집 실패")
                return None
            
            # 데이터 정리
            hist.index = hist.index.tz_localize(None)  # 시간대 제거
            hist['Price_Change_24h'] = hist['Close'].pct_change(24) * 100  # 24시간 변동률
            
            logger.info(f"✅ {coin_id} 데이터 수집 완료: {len(hist)}개 데이터포인트")
            return hist
            
        except Exception as e:
            logger.error(f"{coin_id} 데이터 수집 오류: {str(e)}")
            return None
    
    def get_historical_market_data(self, days: int = 30) -> Dict[str, pd.DataFrame]:
        """거시경제 과거 데이터 수집"""
        market_symbols = {
            'SP500': '^GSPC',
            'VIX': '^VIX', 
            'DXY': 'DX-Y.NYB',
            'GOLD': 'GC=F'
        }
        
        market_data = {}
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        for name, symbol in market_symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=end_date, interval='1d')
                
                if not hist.empty:
                    hist.index = hist.index.tz_localize(None)
                    hist['Daily_Change'] = hist['Close'].pct_change() * 100
                    market_data[name] = hist
                    logger.info(f"✅ {name} 시장 데이터 수집 완료")
                    
            except Exception as e:
                logger.error(f"{name} 시장 데이터 수집 오류: {str(e)}")
        
        return market_data
    
    def get_historical_sentiment_data(self, days: int = 30) -> pd.DataFrame:
        """과거 센티먼트 데이터 수집 (시뮬레이션)"""
        # 실제로는 Fear & Greed Index API의 과거 데이터 사용
        # 여기서는 시뮬레이션 데이터 생성
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 공포탐욕지수 시뮬레이션 (실제 패턴과 유사하게)
        np.random.seed(42)  # 재현 가능한 결과
        
        sentiment_data = []
        for date in date_range:
            # 현실적인 공포탐욕지수 패턴 생성
            base_value = 50
            trend = np.sin((date - start_date).days / 10) * 20  # 주기적 변동
            noise = np.random.normal(0, 10)  # 랜덤 노이즈
            fg_value = max(0, min(100, base_value + trend + noise))
            
            sentiment_data.append({
                'Date': date,
                'Fear_Greed_Index': fg_value,
                'Classification': self._classify_fg_index(fg_value)
            })
        
        df = pd.DataFrame(sentiment_data)
        df.set_index('Date', inplace=True)
        
        logger.info(f"✅ 센티먼트 데이터 시뮬레이션 완료: {len(df)}일")
        return df
    
    def _classify_fg_index(self, value: float) -> str:
        """공포탐욕지수 분류"""
        if value < 25:
            return "Extreme Fear"
        elif value < 45:
            return "Fear"
        elif value < 55:
            return "Neutral"
        elif value < 75:
            return "Greed"
        else:
            return "Extreme Greed"

class PriceDriverValidator:
    """가격 변동 요인 분석 검증기"""
    
    def __init__(self):
        self.data_collector = HistoricalDataCollector()
        self.price_analyzer = PriceDriverAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
    
    def validate_price_predictions(self, coin_id: str, days: int = 30) -> BacktestReport:
        """가격 변동 예측 검증"""
        logger.info(f"📊 {coin_id} 가격 변동 분석 검증 시작 ({days}일)")
        
        # 과거 데이터 수집
        crypto_data = self.data_collector.get_historical_crypto_data(coin_id, days)
        market_data = self.data_collector.get_historical_market_data(days)
        sentiment_data = self.data_collector.get_historical_sentiment_data(days)
        
        if crypto_data is None:
            raise ValueError(f"{coin_id} 데이터 수집 실패")
        
        validation_results = []
        correct_predictions = 0
        movement_type_stats = {}
        factor_stats = {}
        
        # 24시간 단위로 검증 (최소 24시간 데이터 필요)
        for i in range(24, len(crypto_data)):
            try:
                # 현재 시점 데이터
                current_time = crypto_data.index[i]
                current_price = crypto_data.iloc[i]['Close']
                price_24h_ago = crypto_data.iloc[i-24]['Close']
                
                # 실제 변동률
                actual_change = ((current_price - price_24h_ago) / price_24h_ago) * 100
                actual_movement = self._classify_movement(actual_change)
                
                # 과거 가격 데이터 (예측 시점까지)
                price_series = pd.Series(crypto_data.iloc[i-47:i]['Close'].values)
                
                # 예측 수행
                analysis = self.price_analyzer.analyze_price_movement(
                    coin_id=coin_id,
                    current_price=current_price,
                    price_24h_ago=price_24h_ago,
                    price_data=price_series
                )
                
                # 정확도 평가
                predicted_movement = analysis.movement_type
                is_correct = self._evaluate_prediction_accuracy(
                    actual_change, actual_movement, 
                    analysis.price_change_percent, predicted_movement
                )
                
                if is_correct:
                    correct_predictions += 1
                
                # 결과 저장
                validation_result = ValidationResult(
                    date=current_time.strftime('%Y-%m-%d %H:%M'),
                    actual_change=actual_change,
                    predicted_movement=predicted_movement,
                    actual_movement=actual_movement,
                    accuracy=is_correct,
                    confidence=max([f.confidence for f in analysis.primary_factors]) if analysis.primary_factors else 0.5,
                    primary_factors=[f.factor_type for f in analysis.primary_factors]
                )
                validation_results.append(validation_result)
                
                # 통계 업데이트
                if actual_movement not in movement_type_stats:
                    movement_type_stats[actual_movement] = {'total': 0, 'correct': 0}
                movement_type_stats[actual_movement]['total'] += 1
                if is_correct:
                    movement_type_stats[actual_movement]['correct'] += 1
                
                # 요인별 통계
                for factor in analysis.primary_factors:
                    factor_type = factor.factor_type
                    if factor_type not in factor_stats:
                        factor_stats[factor_type] = {'total': 0, 'correct': 0}
                    factor_stats[factor_type]['total'] += 1
                    if is_correct:
                        factor_stats[factor_type]['correct'] += 1
                
            except Exception as e:
                logger.error(f"검증 중 오류 ({current_time}): {str(e)}")
                continue
        
        # 정확도 계산
        total_predictions = len(validation_results)
        accuracy_rate = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        # 변동 유형별 정확도
        movement_accuracy = {}
        for movement, stats in movement_type_stats.items():
            movement_accuracy[movement] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        
        # 요인별 효과성
        factor_effectiveness = {}
        for factor, stats in factor_stats.items():
            factor_effectiveness[factor] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        
        # 요약 생성
        summary = self._generate_validation_summary(
            coin_id, days, total_predictions, correct_predictions, 
            accuracy_rate, movement_accuracy, factor_effectiveness
        )
        
        logger.info(f"✅ 검증 완료: 전체 정확도 {accuracy_rate:.1%}")
        
        return BacktestReport(
            period=f"{days}일",
            total_predictions=total_predictions,
            correct_predictions=correct_predictions,
            accuracy_rate=accuracy_rate,
            movement_type_accuracy=movement_accuracy,
            factor_effectiveness=factor_effectiveness,
            validation_results=validation_results[-10:],  # 최근 10개만
            summary=summary
        )
    
    def _classify_movement(self, change_percent: float) -> str:
        """변동 유형 분류"""
        if change_percent <= -15:
            return 'crash'
        elif change_percent <= -8:
            return 'dump'
        elif change_percent <= -3:
            return 'normal_down'
        elif change_percent >= 15:
            return 'surge'
        elif change_percent >= 8:
            return 'pump'
        elif change_percent >= 3:
            return 'normal_up'
        else:
            return 'stable'
    
    def _evaluate_prediction_accuracy(self, actual_change: float, actual_movement: str,
                                    predicted_change: float, predicted_movement: str) -> bool:
        """예측 정확도 평가"""
        # 1. 방향성 정확도 (상승/하락)
        actual_direction = 'up' if actual_change > 0 else 'down' if actual_change < 0 else 'stable'
        predicted_direction = 'up' if predicted_change > 0 else 'down' if predicted_change < 0 else 'stable'
        
        direction_correct = actual_direction == predicted_direction
        
        # 2. 변동 강도 정확도
        intensity_correct = actual_movement == predicted_movement
        
        # 3. 오차 허용 범위 (±2%)
        error_acceptable = abs(actual_change - predicted_change) <= 2.0
        
        # 최종 정확도: 방향성 + (강도 또는 오차범위)
        return direction_correct and (intensity_correct or error_acceptable)
    
    def _generate_validation_summary(self, coin_id: str, days: int, total: int, correct: int,
                                   accuracy: float, movement_acc: Dict, factor_eff: Dict) -> str:
        """검증 요약 생성"""
        summary = f"📊 {coin_id.upper()} 가격 변동 분석 검증 보고서\n"
        summary += f"검증 기간: {days}일\n"
        summary += f"전체 예측: {total}회\n"
        summary += f"정확한 예측: {correct}회\n"
        summary += f"전체 정확도: {accuracy:.1%}\n\n"
        
        summary += "📈 변동 유형별 정확도:\n"
        for movement, acc in movement_acc.items():
            summary += f"  • {movement}: {acc:.1%}\n"
        
        summary += "\n🔍 요인별 효과성:\n"
        for factor, eff in factor_eff.items():
            summary += f"  • {factor}: {eff:.1%}\n"
        
        # 성능 평가
        if accuracy >= 0.7:
            summary += "\n✅ 우수: 분석 시스템이 높은 정확도를 보여줍니다."
        elif accuracy >= 0.5:
            summary += "\n⚠️ 보통: 분석 시스템이 적절한 성능을 보여줍니다."
        else:
            summary += "\n❌ 개선 필요: 분석 시스템의 정확도 향상이 필요합니다."
        
        return summary

def demo_backtesting():
    """백테스팅 데모"""
    print("🔍 CoinCompass 백테스팅 및 검증 데모")
    print("=" * 60)
    
    validator = PriceDriverValidator()
    
    # 비트코인 30일 검증
    print("📊 비트코인 30일 검증 중...")
    try:
        report = validator.validate_price_predictions("bitcoin", days=30)
        
        print(f"\n📋 검증 결과:")
        print(f"전체 정확도: {report.accuracy_rate:.1%}")
        print(f"총 예측 횟수: {report.total_predictions}")
        print(f"정확한 예측: {report.correct_predictions}")
        
        print(f"\n🎯 변동 유형별 정확도:")
        for movement, accuracy in report.movement_type_accuracy.items():
            print(f"  {movement}: {accuracy:.1%}")
        
        print(f"\n🔧 요인별 효과성:")
        for factor, effectiveness in report.factor_effectiveness.items():
            print(f"  {factor}: {effectiveness:.1%}")
        
        print(f"\n📝 요약:")
        print(report.summary)
        
    except Exception as e:
        logger.error(f"백테스팅 데모 오류: {str(e)}")
        print(f"❌ 백테스팅 오류: {str(e)}")

if __name__ == "__main__":
    demo_backtesting()