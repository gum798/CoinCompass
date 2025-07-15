"""
데이터 모델 정의
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
from decimal import Decimal

@dataclass
class PriceData:
    """가격 데이터 모델"""
    price: float
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    price_change_24h: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "unknown"
    
    def to_dict(self) -> Dict:
        return {
            'price': self.price,
            'market_cap': self.market_cap,
            'volume_24h': self.volume_24h,
            'price_change_24h': self.price_change_24h,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }

@dataclass
class CoinData:
    """코인 정보 모델"""
    id: str
    symbol: str
    name: str
    current_price: PriceData
    rank: Optional[int] = None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'current_price': self.current_price.to_dict(),
            'rank': self.rank
        }

@dataclass
class TechnicalIndicators:
    """기술적 지표 모델"""
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    sma_short: Optional[float] = None
    sma_long: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_lower: Optional[float] = None
    bollinger_middle: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

@dataclass
class TradingSignal:
    """매매 신호 모델"""
    signal: str  # BUY, SELL, HOLD
    confidence: float  # 0.0 ~ 1.0
    indicators_used: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    reason: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'signal': self.signal,
            'confidence': self.confidence,
            'indicators_used': self.indicators_used,
            'timestamp': self.timestamp.isoformat(),
            'reason': self.reason
        }

@dataclass
class AnalysisResult:
    """분석 결과 모델"""
    coin_id: str
    price_data: PriceData
    technical_indicators: TechnicalIndicators
    trading_signal: TradingSignal
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'coin_id': self.coin_id,
            'price_data': self.price_data.to_dict(),
            'technical_indicators': self.technical_indicators.to_dict(),
            'trading_signal': self.trading_signal.to_dict(),
            'analysis_timestamp': self.analysis_timestamp.isoformat()
        }

@dataclass
class MarketSentiment:
    """시장 센티먼트 모델"""
    fear_greed_index: Optional[int] = None
    social_sentiment: Optional[float] = None  # -1.0 ~ 1.0
    news_sentiment: Optional[float] = None    # -1.0 ~ 1.0
    funding_rate: Optional[float] = None
    long_short_ratio: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() 
                if v is not None and k != 'timestamp'} | {
            'timestamp': self.timestamp.isoformat()
        }