"""
기술적 분석 모듈
기존 technical_indicators.py를 개선하여 재구조화
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List

from ..core.models import TechnicalIndicators, TradingSignal
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TechnicalAnalyzer:
    """기술적 분석기"""
    
    def __init__(self):
        self.indicators = {}
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_sma(self, prices: pd.Series, period: int = 20) -> pd.Series:
        """단순 이동평균 계산"""
        return prices.rolling(window=period).mean()
    
    def calculate_ema(self, prices: pd.Series, period: int = 20) -> pd.Series:
        """지수 이동평균 계산"""
        return prices.ewm(span=period).mean()
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """MACD 계산"""
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """볼린저 밴드 계산"""
        sma = self.calculate_sma(prices, period)
        std = prices.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
    
    def analyze_price_data(self, price_data: pd.Series) -> TechnicalIndicators:
        """가격 데이터 종합 분석"""
        if len(price_data) < 26:  # MACD 계산을 위한 최소 데이터
            logger.warning("기술적 분석을 위한 데이터가 부족합니다")
            return TechnicalIndicators()
        
        # 각 지표 계산
        rsi = self.calculate_rsi(price_data)
        sma_short = self.calculate_sma(price_data, 5)
        sma_long = self.calculate_sma(price_data, 20)
        macd_data = self.calculate_macd(price_data)
        bollinger = self.calculate_bollinger_bands(price_data)
        
        # 최신 값들 추출
        latest_idx = -1
        
        indicators = TechnicalIndicators(
            rsi=rsi.iloc[latest_idx] if not pd.isna(rsi.iloc[latest_idx]) else None,
            macd=macd_data['macd'].iloc[latest_idx] if not pd.isna(macd_data['macd'].iloc[latest_idx]) else None,
            macd_signal=macd_data['signal'].iloc[latest_idx] if not pd.isna(macd_data['signal'].iloc[latest_idx]) else None,
            sma_short=sma_short.iloc[latest_idx] if not pd.isna(sma_short.iloc[latest_idx]) else None,
            sma_long=sma_long.iloc[latest_idx] if not pd.isna(sma_long.iloc[latest_idx]) else None,
            bollinger_upper=bollinger['upper'].iloc[latest_idx] if not pd.isna(bollinger['upper'].iloc[latest_idx]) else None,
            bollinger_lower=bollinger['lower'].iloc[latest_idx] if not pd.isna(bollinger['lower'].iloc[latest_idx]) else None,
            bollinger_middle=bollinger['middle'].iloc[latest_idx] if not pd.isna(bollinger['middle'].iloc[latest_idx]) else None
        )
        
        return indicators
    
    def generate_trading_signal(self, price_data: pd.Series, indicators: TechnicalIndicators) -> TradingSignal:
        """매매 신호 생성"""
        signals = []
        reasons = []
        confidence_scores = []
        
        current_price = price_data.iloc[-1]
        
        # RSI 신호
        if indicators.rsi is not None:
            if indicators.rsi < 30:
                signals.append('BUY')
                reasons.append(f'RSI 과매도 ({indicators.rsi:.1f})')
                confidence_scores.append(0.8)
            elif indicators.rsi > 70:
                signals.append('SELL')
                reasons.append(f'RSI 과매수 ({indicators.rsi:.1f})')
                confidence_scores.append(0.8)
        
        # MACD 신호
        if indicators.macd is not None and indicators.macd_signal is not None:
            if indicators.macd > indicators.macd_signal:
                if len(price_data) > 1:
                    prev_macd = self.calculate_macd(price_data)['macd'].iloc[-2]
                    prev_signal = self.calculate_macd(price_data)['signal'].iloc[-2]
                    if prev_macd <= prev_signal:  # 골든크로스
                        signals.append('BUY')
                        reasons.append('MACD 골든크로스')
                        confidence_scores.append(0.7)
            else:
                if len(price_data) > 1:
                    prev_macd = self.calculate_macd(price_data)['macd'].iloc[-2]
                    prev_signal = self.calculate_macd(price_data)['signal'].iloc[-2]
                    if prev_macd >= prev_signal:  # 데드크로스
                        signals.append('SELL')
                        reasons.append('MACD 데드크로스')
                        confidence_scores.append(0.7)
        
        # 이동평균 신호
        if indicators.sma_short is not None and indicators.sma_long is not None:
            if indicators.sma_short > indicators.sma_long:
                signals.append('BUY')
                reasons.append('단기MA > 장기MA')
                confidence_scores.append(0.6)
            else:
                signals.append('SELL')
                reasons.append('단기MA < 장기MA')
                confidence_scores.append(0.6)
        
        # 볼린저 밴드 신호
        if indicators.bollinger_upper is not None and indicators.bollinger_lower is not None:
            if current_price > indicators.bollinger_upper:
                signals.append('SELL')
                reasons.append('볼린저 상단 돌파')
                confidence_scores.append(0.5)
            elif current_price < indicators.bollinger_lower:
                signals.append('BUY')
                reasons.append('볼린저 하단 터치')
                confidence_scores.append(0.5)
        
        # 최종 신호 결정
        if not signals:
            final_signal = 'HOLD'
            confidence = 0.5
            reason = '명확한 신호 없음'
        else:
            buy_count = signals.count('BUY')
            sell_count = signals.count('SELL')
            
            if buy_count > sell_count:
                final_signal = 'BUY'
                confidence = np.mean([conf for sig, conf in zip(signals, confidence_scores) if sig == 'BUY'])
                reason = ', '.join([r for sig, r in zip(signals, reasons) if sig == 'BUY'])
            elif sell_count > buy_count:
                final_signal = 'SELL'
                confidence = np.mean([conf for sig, conf in zip(signals, confidence_scores) if sig == 'SELL'])
                reason = ', '.join([r for sig, r in zip(signals, reasons) if sig == 'SELL'])
            else:
                final_signal = 'HOLD'
                confidence = 0.5
                reason = '상충되는 신호들'
        
        indicators_used = []
        if indicators.rsi is not None:
            indicators_used.append('RSI')
        if indicators.macd is not None:
            indicators_used.append('MACD')
        if indicators.sma_short is not None:
            indicators_used.append('이동평균')
        if indicators.bollinger_upper is not None:
            indicators_used.append('볼린저밴드')
        
        return TradingSignal(
            signal=final_signal,
            confidence=min(confidence, 1.0),
            indicators_used=indicators_used,
            reason=reason
        )