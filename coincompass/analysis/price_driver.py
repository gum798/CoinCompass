"""
가격 변동 요인 분석 모듈
코인 가격 변동의 주요 원인을 분석하고 일반인이 이해하기 쉬운 설명 제공
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from .market_analyzer import MarketAnalyzer
from .technical import TechnicalAnalyzer
from .onchain import SentimentAnalyzer
from .macro import MacroeconomicAnalyzer
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class PriceMovementFactor:
    """가격 변동 요인"""
    factor_type: str  # 'technical', 'macro', 'sentiment', 'news'
    impact_score: float  # -1.0 ~ 1.0 (음수는 하락 요인, 양수는 상승 요인)
    confidence: float  # 0.0 ~ 1.0
    description: str  # 일반인용 설명
    technical_reason: str  # 기술적 근거

@dataclass
class PriceMovementAnalysis:
    """가격 변동 분석 결과"""
    price_change_percent: float
    movement_type: str  # 'surge', 'pump', 'normal_up', 'normal_down', 'dump', 'crash'
    primary_factors: List[PriceMovementFactor]
    summary: str
    recommendation: str
    confidence: float  # 0.0 ~ 1.0 (분석 신뢰도)

class PriceDriverAnalyzer:
    """가격 변동 요인 분석기"""
    
    def __init__(self):
        self.market_analyzer = MarketAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.macro_analyzer = MacroeconomicAnalyzer()
        
        # 가격 변동 임계값 정의
        self.movement_thresholds = {
            'crash': -15.0,      # 15% 이상 하락
            'dump': -8.0,        # 8% 이상 하락
            'normal_down': -3.0, # 3% 이상 하락
            'normal_up': 3.0,    # 3% 이상 상승
            'pump': 8.0,         # 8% 이상 상승
            'surge': 15.0        # 15% 이상 상승
        }
    
    def analyze_price_movement(self, coin_id: str, current_price: float, 
                             price_24h_ago: float, price_data: pd.Series = None,
                             fred_api_key: Optional[str] = None) -> PriceMovementAnalysis:
        """가격 변동 요인 종합 분석"""
        
        # 가격 변동률 계산
        price_change = ((current_price - price_24h_ago) / price_24h_ago) * 100
        
        # 변동 유형 분류
        movement_type = self._classify_movement(price_change)
        
        logger.info(f"📊 {coin_id} 가격 변동 분석: {price_change:+.2f}% ({movement_type})")
        
        # 변동이 미미한 경우 간단 분석
        if abs(price_change) < 1.0:
            return PriceMovementAnalysis(
                price_change_percent=price_change,
                movement_type="stable",
                primary_factors=[],
                summary="가격이 안정적으로 유지되고 있습니다.",
                recommendation="현재 상황을 지켜보세요.",
                confidence=0.8  # 안정적인 상황이므로 높은 신뢰도
            )
        
        # 주요 요인 분석
        factors = []
        
        # 1. 기술적 요인 분석
        if price_data is not None:
            tech_factor = self._analyze_technical_factors(price_data, price_change)
            if tech_factor:
                factors.append(tech_factor)
        
        # 2. 센티먼트 요인 분석
        sentiment_factor = self._analyze_sentiment_factors(price_change)
        if sentiment_factor:
            factors.append(sentiment_factor)
        
        # 3. 거시경제 요인 분석
        macro_factor = self._analyze_macro_factors(price_change, fred_api_key)
        if macro_factor:
            factors.append(macro_factor)
        
        # 4. 시장 구조적 요인 분석
        structural_factor = self._analyze_structural_factors(price_change, movement_type)
        if structural_factor:
            factors.append(structural_factor)
        
        # 요인별 중요도 정렬
        factors.sort(key=lambda x: abs(x.impact_score) * x.confidence, reverse=True)
        
        # 요약 및 추천 생성
        summary = self._generate_movement_summary(price_change, movement_type, factors)
        recommendation = self._generate_recommendation(movement_type, factors)
        
        # 전체 신뢰도 계산 (주요 요인들의 가중 평균)
        if factors:
            confidence = sum(factor.confidence * abs(factor.impact_score) for factor in factors[:3]) / sum(abs(factor.impact_score) for factor in factors[:3])
        else:
            confidence = 0.5  # 기본값
        
        return PriceMovementAnalysis(
            price_change_percent=price_change,
            movement_type=movement_type,
            primary_factors=factors[:3],  # 상위 3개 요인만
            summary=summary,
            recommendation=recommendation,
            confidence=min(1.0, max(0.0, confidence))  # 0.0 ~ 1.0 범위 보장
        )
    
    def _classify_movement(self, price_change: float) -> str:
        """가격 변동 유형 분류"""
        if price_change <= self.movement_thresholds['crash']:
            return 'crash'
        elif price_change <= self.movement_thresholds['dump']:
            return 'dump'
        elif price_change <= self.movement_thresholds['normal_down']:
            return 'normal_down'
        elif price_change >= self.movement_thresholds['surge']:
            return 'surge'
        elif price_change >= self.movement_thresholds['pump']:
            return 'pump'
        elif price_change >= self.movement_thresholds['normal_up']:
            return 'normal_up'
        else:
            return 'stable'
    
    def _analyze_technical_factors(self, price_data: pd.Series, price_change: float) -> Optional[PriceMovementFactor]:
        """기술적 요인 분석"""
        try:
            # 데이터 유효성 검사
            if price_data is None or len(price_data) < 5:
                logger.warning("기술적 분석에 충분한 가격 데이터가 없습니다")
                return None
            
            indicators = self.technical_analyzer.analyze_price_data(price_data)
            signal = self.technical_analyzer.generate_trading_signal(price_data, indicators)
            
            if not indicators or not signal:
                return None
            
            # RSI 기반 분석
            rsi_impact = 0.0
            rsi_desc = ""
            
            if indicators.rsi:
                if indicators.rsi > 70:
                    rsi_impact = -0.6  # 과매수 구간
                    rsi_desc = "과매수 구간에서 차익실현 매물이 나오고 있어요"
                elif indicators.rsi < 30:
                    rsi_impact = 0.6   # 과매도 구간
                    rsi_desc = "과매도 구간에서 저점 매수세가 유입되고 있어요"
                elif indicators.rsi > 50:
                    rsi_impact = 0.3   # 상승 모멘텀
                    rsi_desc = "상승 모멘텀이 강해지고 있어요"
                else:
                    rsi_impact = -0.3  # 하락 모멘텀
                    rsi_desc = "하락 모멘텀이 나타나고 있어요"
            
            # MACD 기반 분석
            macd_impact = 0.0
            macd_desc = ""
            
            if indicators.macd and indicators.macd_signal:
                macd_diff = indicators.macd - indicators.macd_signal
                if macd_diff > 0 and price_change > 0:
                    macd_impact = 0.4
                    macd_desc = "매수 신호가 나타나 상승을 이끌고 있어요"
                elif macd_diff < 0 and price_change < 0:
                    macd_impact = -0.4
                    macd_desc = "매도 신호가 나타나 하락을 이끌고 있어요"
            
            # 종합 기술적 영향도
            total_impact = (rsi_impact + macd_impact) / 2
            
            # 설명 조합
            descriptions = [desc for desc in [rsi_desc, macd_desc] if desc]
            final_desc = descriptions[0] if descriptions else "기술적 지표에 따른 움직임이에요"
            
            return PriceMovementFactor(
                factor_type="technical",
                impact_score=total_impact,
                confidence=signal.confidence if signal.confidence else 0.5,
                description=final_desc,
                technical_reason=f"RSI: {indicators.rsi:.1f}, MACD: {signal.signal}"
            )
            
        except Exception as e:
            logger.error(f"기술적 요인 분석 오류: {str(e)}")
            return None
    
    def _analyze_sentiment_factors(self, price_change: float) -> Optional[PriceMovementFactor]:
        """센티먼트 요인 분석"""
        try:
            sentiment = self.sentiment_analyzer.get_comprehensive_sentiment()
            
            impact_score = 0.0
            description = ""
            confidence = 0.5
            
            # 공포탐욕지수 분석
            if sentiment.fear_greed_index:
                fg_index = sentiment.fear_greed_index
                
                if fg_index > 75:  # 극탐욕
                    if price_change > 0:
                        impact_score = 0.7
                        description = "시장이 극도로 탐욕적이어서 FOMO(놓칠까봐 하는 두려움) 매수가 몰리고 있어요"
                    else:
                        impact_score = -0.8
                        description = "극탐욕 상태에서 갑작스런 차익실현이 몰리면서 급락하고 있어요"
                    confidence = 0.8
                    
                elif fg_index < 25:  # 극공포
                    if price_change < 0:
                        impact_score = -0.7
                        description = "시장이 극도로 공포스러워서 패닉 매도가 이어지고 있어요"
                    else:
                        impact_score = 0.8
                        description = "극공포 상태에서 용감한 저점 매수세가 유입되고 있어요"
                    confidence = 0.8
                    
                elif fg_index > 60:  # 탐욕
                    impact_score = 0.4 if price_change > 0 else -0.3
                    description = "시장 심리가 탐욕적이어서 강세 분위기가 형성되고 있어요"
                    confidence = 0.6
                    
                elif fg_index < 40:  # 공포
                    impact_score = -0.4 if price_change < 0 else 0.3
                    description = "시장 심리가 공포스러워서 약세 분위기가 지배적이에요"
                    confidence = 0.6
            
            # 소셜 센티먼트 추가 고려
            if sentiment.social_sentiment:
                if sentiment.social_sentiment > 0.2:
                    description += " 소셜미디어에서도 긍정적인 반응이 많아요"
                elif sentiment.social_sentiment < -0.2:
                    description += " 소셜미디어에서도 부정적인 반응이 많아요"
            
            if abs(impact_score) > 0.1:
                return PriceMovementFactor(
                    factor_type="sentiment",
                    impact_score=impact_score,
                    confidence=confidence,
                    description=description,
                    technical_reason=f"공포탐욕지수: {sentiment.fear_greed_index}"
                )
            
        except Exception as e:
            logger.error(f"센티먼트 요인 분석 오류: {str(e)}")
        
        return None
    
    def _analyze_macro_factors(self, price_change: float, fred_api_key: Optional[str] = None) -> Optional[PriceMovementFactor]:
        """거시경제 요인 분석"""
        try:
            indicators = self.macro_analyzer.get_economic_indicators(fred_api_key)
            signals = self.macro_analyzer.calculate_crypto_correlation_signals(indicators)
            
            if not signals:
                return None
            
            # 주요 거시경제 신호 분석
            total_signal = sum(signals.values()) / len(signals)
            impact_score = total_signal * 2  # 신호를 임팩트로 변환
            
            descriptions = []
            confidence = 0.5
            
            # 개별 요인 분석
            if 'tech_stock_momentum' in signals:
                tech_signal = signals['tech_stock_momentum']
                if abs(tech_signal) > 0.3:
                    if tech_signal > 0:
                        descriptions.append("나스닥 등 기술주가 강세를 보이면서 위험자산 선호 심리가 높아졌어요")
                    else:
                        descriptions.append("나스닥 등 기술주가 약세를 보이면서 위험자산 회피 심리가 강해졌어요")
                    confidence += 0.2
            
            if 'dollar_inverse_correlation' in signals:
                dollar_signal = signals['dollar_inverse_correlation']
                if abs(dollar_signal) > 0.3:
                    if dollar_signal > 0:
                        descriptions.append("달러 약세로 대안 투자처로서 암호화폐 매력이 증가했어요")
                    else:
                        descriptions.append("달러 강세로 상대적으로 암호화폐 매력이 감소했어요")
                    confidence += 0.2
            
            if 'risk_sentiment' in signals:
                risk_signal = signals['risk_sentiment']
                if abs(risk_signal) > 0.3:
                    if risk_signal > 0:
                        descriptions.append("VIX 하락으로 시장 불안이 완화되어 위험자산 투자가 늘었어요")
                    else:
                        descriptions.append("VIX 상승으로 시장 불안이 커져 안전자산으로 자금이 이동했어요")
                    confidence += 0.2
            
            # 설명 조합
            if descriptions:
                final_desc = descriptions[0]
                if len(descriptions) > 1:
                    final_desc += f" 또한 {descriptions[1]}"
            else:
                if impact_score > 0:
                    final_desc = "전반적인 거시경제 환경이 암호화폐에 우호적으로 변화했어요"
                else:
                    final_desc = "전반적인 거시경제 환경이 암호화폐에 부정적으로 변화했어요"
            
            if abs(impact_score) > 0.1:
                return PriceMovementFactor(
                    factor_type="macro",
                    impact_score=max(-1.0, min(1.0, impact_score)),
                    confidence=min(1.0, confidence),
                    description=final_desc,
                    technical_reason=f"거시경제 신호: {total_signal:+.2f}"
                )
            
        except Exception as e:
            logger.error(f"거시경제 요인 분석 오류: {str(e)}")
        
        return None
    
    def _analyze_structural_factors(self, price_change: float, movement_type: str) -> Optional[PriceMovementFactor]:
        """시장 구조적 요인 분석"""
        
        # 극단적 움직임의 경우 구조적 요인 추정
        if movement_type in ['crash', 'dump']:
            return PriceMovementFactor(
                factor_type="structural",
                impact_score=-0.6,
                confidence=0.7,
                description="대량 매도나 청산, 또는 악재 뉴스로 인한 급락이 발생했을 가능성이 높아요",
                technical_reason=f"급락 패턴: {movement_type}"
            )
        
        elif movement_type in ['surge', 'pump']:
            return PriceMovementFactor(
                factor_type="structural", 
                impact_score=0.6,
                confidence=0.7,
                description="대량 매수나 호재 뉴스, 또는 기관 투자 유입으로 인한 급등이 발생했을 가능성이 높아요",
                technical_reason=f"급등 패턴: {movement_type}"
            )
        
        # 일반적인 변동의 경우 거래량 기반 추정
        elif abs(price_change) > 2:
            if price_change > 0:
                return PriceMovementFactor(
                    factor_type="structural",
                    impact_score=0.3,
                    confidence=0.4,
                    description="평소보다 많은 매수 주문이 들어와서 가격이 상승했어요",
                    technical_reason="매수 우세"
                )
            else:
                return PriceMovementFactor(
                    factor_type="structural",
                    impact_score=-0.3,
                    confidence=0.4,
                    description="평소보다 많은 매도 주문이 들어와서 가격이 하락했어요",
                    technical_reason="매도 우세"
                )
        
        return None
    
    def _generate_movement_summary(self, price_change: float, movement_type: str, 
                                 factors: List[PriceMovementFactor]) -> str:
        """가격 변동 요약 생성"""
        
        # 기본 변동 설명
        movement_descriptions = {
            'crash': f"📉 {abs(price_change):.1f}% 급락했습니다",
            'dump': f"📉 {abs(price_change):.1f}% 크게 하락했습니다", 
            'normal_down': f"📉 {abs(price_change):.1f}% 하락했습니다",
            'normal_up': f"📈 {price_change:.1f}% 상승했습니다",
            'pump': f"📈 {price_change:.1f}% 크게 상승했습니다",
            'surge': f"🚀 {price_change:.1f}% 급등했습니다",
            'stable': "💤 가격이 안정적입니다"
        }
        
        summary = movement_descriptions.get(movement_type, f"{price_change:+.1f}% 변동했습니다")
        
        # 주요 요인 설명 추가
        if factors:
            primary_factor = factors[0]
            summary += f"\n\n🔍 주요 원인: {primary_factor.description}"
            
            if len(factors) > 1:
                secondary_factor = factors[1]
                summary += f"\n\n🔸 추가 요인: {secondary_factor.description}"
        
        return summary
    
    def _generate_recommendation(self, movement_type: str, 
                               factors: List[PriceMovementFactor]) -> str:
        """투자 추천 생성"""
        
        if movement_type in ['crash', 'dump']:
            return "⚠️ 급락 상황입니다. 패닉 매도는 피하고 상황을 지켜본 후 판단하세요."
        
        elif movement_type in ['surge', 'pump']:
            return "🚨 급등 상황입니다. FOMO 매수보다는 조정을 기다려 보세요."
        
        elif movement_type in ['normal_up']:
            primary_impact = factors[0].impact_score if factors else 0
            if primary_impact > 0.5:
                return "📈 상승 모멘텀이 강합니다. 추가 상승 가능성을 고려해보세요."
            else:
                return "📈 적당한 상승입니다. 목표가 도달 시 수익 실현을 고려하세요."
        
        elif movement_type in ['normal_down']:
            primary_impact = factors[0].impact_score if factors else 0
            if primary_impact < -0.5:
                return "📉 하락 모멘텀이 강합니다. 손절매를 고려하거나 대기하세요."
            else:
                return "📉 일시적 조정일 수 있습니다. 장기 관점에서 판단하세요."
        
        else:
            return "💡 현재 상황을 지켜보며 기회를 기다리세요."

def demo_price_driver_analysis():
    """가격 변동 요인 분석 데모"""
    print("📊 가격 변동 요인 분석 데모")
    print("=" * 60)
    
    analyzer = PriceDriverAnalyzer()
    
    # 샘플 데이터로 테스트
    import numpy as np
    
    # 급등 시나리오
    print("\n🚀 급등 시나리오 분석:")
    current_price = 50000
    price_24h_ago = 42000
    sample_prices = pd.Series(np.linspace(42000, 50000, 50))
    
    analysis = analyzer.analyze_price_movement(
        coin_id="bitcoin",
        current_price=current_price,
        price_24h_ago=price_24h_ago,
        price_data=sample_prices
    )
    
    print(f"변동률: {analysis.price_change_percent:+.2f}%")
    print(f"변동 유형: {analysis.movement_type}")
    print(f"요약: {analysis.summary}")
    print(f"추천: {analysis.recommendation}")
    
    if analysis.primary_factors:
        print("\n주요 요인들:")
        for i, factor in enumerate(analysis.primary_factors, 1):
            print(f"{i}. {factor.description}")
            print(f"   영향도: {factor.impact_score:+.2f}, 신뢰도: {factor.confidence:.1%}")
    
    # 급락 시나리오
    print("\n\n📉 급락 시나리오 분석:")
    current_price = 35000
    price_24h_ago = 42000
    sample_prices = pd.Series(np.linspace(42000, 35000, 50))
    
    analysis = analyzer.analyze_price_movement(
        coin_id="bitcoin",
        current_price=current_price,
        price_24h_ago=price_24h_ago,
        price_data=sample_prices
    )
    
    print(f"변동률: {analysis.price_change_percent:+.2f}%")
    print(f"변동 유형: {analysis.movement_type}")
    print(f"요약: {analysis.summary}")
    print(f"추천: {analysis.recommendation}")
    
    if analysis.primary_factors:
        print("\n주요 요인들:")
        for i, factor in enumerate(analysis.primary_factors, 1):
            print(f"{i}. {factor.description}")
            print(f"   영향도: {factor.impact_score:+.2f}, 신뢰도: {factor.confidence:.1%}")

if __name__ == "__main__":
    demo_price_driver_analysis()