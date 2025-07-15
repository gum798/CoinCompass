"""
통합 마켓 분석기
온체인, 거시경제, 센티먼트 분석을 통합하여 종합적인 시장 분석 제공
"""

import asyncio
from datetime import datetime
from typing import Dict, Optional, Any, List
import pandas as pd

from .technical import TechnicalAnalyzer
from .onchain import OnChainAnalyzer, SentimentAnalyzer
from .macro import MacroeconomicAnalyzer
from ..utils.logger import get_logger
from ..config.settings import Settings

logger = get_logger(__name__)

class MarketAnalyzer:
    """통합 마켓 분석기"""
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        
        # 개별 분석기 초기화
        self.technical_analyzer = TechnicalAnalyzer()
        self.onchain_analyzer = OnChainAnalyzer(settings)
        self.macro_analyzer = MacroeconomicAnalyzer(settings)
        self.sentiment_analyzer = SentimentAnalyzer()
        
    def get_comprehensive_analysis(self, coin_id: str, price_data: pd.Series = None, 
                                 fred_api_key: Optional[str] = None,
                                 etherscan_api_key: Optional[str] = None) -> Dict[str, Any]:
        """종합적인 시장 분석"""
        logger.info(f"📊 {coin_id} 종합 분석 시작...")
        
        analysis_result = {
            'coin_id': coin_id,
            'timestamp': datetime.now().isoformat(),
            'technical': None,
            'onchain': None,
            'macro': None,
            'sentiment': None,
            'summary': None
        }
        
        try:
            # 1. 기술적 분석
            if price_data is not None:
                logger.info("🔍 기술적 분석 수행 중...")
                indicators = self.technical_analyzer.analyze_price_data(price_data)
                signal = self.technical_analyzer.generate_trading_signal(price_data, indicators)
                
                analysis_result['technical'] = {
                    'indicators': indicators.__dict__ if indicators else None,
                    'signal': signal.__dict__ if signal else None
                }
                logger.info("✅ 기술적 분석 완료")
            
            # 2. 온체인 분석
            logger.info("🔗 온체인 분석 수행 중...")
            blockchain_metrics = self.onchain_analyzer.get_blockchain_metrics()
            network_health = self.onchain_analyzer.analyze_network_health(blockchain_metrics)
            
            analysis_result['onchain'] = {
                'metrics': blockchain_metrics,
                'health_analysis': network_health
            }
            logger.info("✅ 온체인 분석 완료")
            
            # 3. 거시경제 분석
            logger.info("📈 거시경제 분석 수행 중...")
            economic_indicators = self.macro_analyzer.get_economic_indicators(fred_api_key)
            market_conditions = self.macro_analyzer.analyze_market_conditions(economic_indicators)
            correlation_signals = self.macro_analyzer.calculate_crypto_correlation_signals(economic_indicators)
            
            analysis_result['macro'] = {
                'indicators': economic_indicators,
                'conditions': market_conditions,
                'correlation_signals': correlation_signals
            }
            logger.info("✅ 거시경제 분석 완료")
            
            # 4. 센티먼트 분석
            logger.info("😰 센티먼트 분석 수행 중...")
            sentiment = self.sentiment_analyzer.get_comprehensive_sentiment()
            
            analysis_result['sentiment'] = {
                'fear_greed_index': sentiment.fear_greed_index,
                'social_sentiment': sentiment.social_sentiment
            }
            logger.info("✅ 센티먼트 분석 완료")
            
            # 5. 종합 요약 생성
            analysis_result['summary'] = self._generate_comprehensive_summary(analysis_result)
            
            logger.info("🎯 종합 분석 완료")
            
        except Exception as e:
            logger.error(f"❌ 종합 분석 중 오류: {str(e)}")
            analysis_result['error'] = str(e)
        
        return analysis_result
    
    def _generate_comprehensive_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """종합 분석 요약 생성"""
        summary = {
            'overall_score': 0.0,
            'recommendation': 'HOLD',
            'confidence': 0.5,
            'key_factors': [],
            'risks': [],
            'opportunities': []
        }
        
        scores = []
        
        # 기술적 분석 점수
        if analysis.get('technical') and analysis['technical'].get('signal'):
            signal = analysis['technical']['signal']
            if signal.get('signal') == 'BUY':
                tech_score = 0.7 + (signal.get('confidence', 0) * 0.3)
                summary['key_factors'].append(f"기술적 매수 신호 (신뢰도: {signal.get('confidence', 0):.1%})")
            elif signal.get('signal') == 'SELL':
                tech_score = 0.3 - (signal.get('confidence', 0) * 0.3)
                summary['risks'].append(f"기술적 매도 신호 (신뢰도: {signal.get('confidence', 0):.1%})")
            else:
                tech_score = 0.5
            scores.append(tech_score)
        
        # 거시경제 점수
        if analysis.get('macro') and analysis['macro'].get('correlation_signals'):
            signals = analysis['macro']['correlation_signals']
            macro_score = 0.5 + (sum(signals.values()) / len(signals)) if signals else 0.5
            
            if macro_score > 0.6:
                summary['opportunities'].append("거시경제 환경이 암호화폐에 우호적")
            elif macro_score < 0.4:
                summary['risks'].append("거시경제 환경이 암호화폐에 부정적")
            
            scores.append(max(0, min(1, macro_score)))
        
        # 센티먼트 점수
        if analysis.get('sentiment'):
            sentiment_data = analysis['sentiment']
            
            # 공포탐욕지수 점수 (0-100을 0-1로 변환)
            if sentiment_data.get('fear_greed_index'):
                fg_score = sentiment_data['fear_greed_index'] / 100
                if fg_score < 0.2:
                    summary['opportunities'].append("극도의 공포 상태 - 매수 기회")
                elif fg_score > 0.8:
                    summary['risks'].append("극도의 탐욕 상태 - 조정 위험")
                scores.append(fg_score)
            
            # 소셜 센티먼트 점수
            if sentiment_data.get('social_sentiment') is not None:
                social_score = 0.5 + sentiment_data['social_sentiment']
                scores.append(max(0, min(1, social_score)))
        
        # 온체인 건강도 (정성적 평가)
        if analysis.get('onchain') and analysis['onchain'].get('health_analysis'):
            health = analysis['onchain']['health_analysis']
            if '높음' in str(health.values()) or '빠름' in str(health.values()):
                summary['key_factors'].append("네트워크 활동 증가")
            elif '느림' in str(health.values()) or '혼잡' in str(health.values()):
                summary['risks'].append("네트워크 혼잡 상태")
        
        # 종합 점수 계산
        if scores:
            summary['overall_score'] = sum(scores) / len(scores)
            summary['confidence'] = min(len(scores) / 4, 1.0)  # 4개 요소 모두 있으면 신뢰도 최대
            
            # 추천 결정
            if summary['overall_score'] > 0.65:
                summary['recommendation'] = 'BUY'
            elif summary['overall_score'] < 0.35:
                summary['recommendation'] = 'SELL'
            else:
                summary['recommendation'] = 'HOLD'
        
        return summary
    
    def get_market_overview(self, coins: List[str], fred_api_key: Optional[str] = None) -> Dict[str, Any]:
        """전체 시장 개요"""
        logger.info("🌍 시장 전체 개요 분석 시작...")
        
        overview = {
            'timestamp': datetime.now().isoformat(),
            'macro_environment': None,
            'sentiment_overview': None,
            'network_status': None,
            'market_summary': None
        }
        
        try:
            # 거시경제 환경
            economic_data = self.macro_analyzer.get_economic_indicators(fred_api_key)
            overview['macro_environment'] = self.macro_analyzer.generate_macro_summary(economic_data)
            
            # 전체 센티먼트
            sentiment = self.sentiment_analyzer.get_comprehensive_sentiment()
            overview['sentiment_overview'] = {
                'fear_greed': sentiment.fear_greed_index,
                'social_sentiment': sentiment.social_sentiment
            }
            
            # 네트워크 상태
            blockchain_metrics = self.onchain_analyzer.get_blockchain_metrics()
            overview['network_status'] = self.onchain_analyzer.analyze_network_health(blockchain_metrics)
            
            # 시장 요약
            overview['market_summary'] = self._generate_market_summary(overview)
            
            logger.info("✅ 시장 개요 분석 완료")
            
        except Exception as e:
            logger.error(f"❌ 시장 개요 분석 중 오류: {str(e)}")
            overview['error'] = str(e)
        
        return overview
    
    def _generate_market_summary(self, overview: Dict[str, Any]) -> str:
        """시장 요약 텍스트 생성"""
        summary_parts = ["📊 시장 현황 요약:"]
        
        # 센티먼트 요약
        if overview.get('sentiment_overview'):
            sentiment = overview['sentiment_overview']
            if sentiment.get('fear_greed'):
                fg_value = sentiment['fear_greed']
                if fg_value < 25:
                    summary_parts.append("• 시장 심리: 극도의 공포 상태")
                elif fg_value > 75:
                    summary_parts.append("• 시장 심리: 극도의 탐욕 상태")
                else:
                    summary_parts.append(f"• 시장 심리: 보통 수준 (공포탐욕지수: {fg_value})")
        
        # 네트워크 상태 요약
        if overview.get('network_status'):
            network = overview['network_status']
            if network:
                summary_parts.append("• 네트워크: " + ", ".join([f"{k}({v})" for k, v in network.items()]))
        
        # 거시경제 요약 (이미 텍스트 형태)
        if overview.get('macro_environment'):
            summary_parts.append("• 거시경제 환경이 분석되었습니다")
        
        return "\n".join(summary_parts)

def demo_comprehensive_analysis():
    """종합 분석 데모"""
    print("🧭 CoinCompass 종합 시장 분석 데모")
    print("=" * 60)
    
    analyzer = MarketAnalyzer()
    
    # 샘플 가격 데이터 생성
    import numpy as np
    sample_prices = pd.Series(np.random.normal(100, 5, 100).cumsum())
    
    print("📊 비트코인 종합 분석 중...")
    analysis = analyzer.get_comprehensive_analysis("bitcoin", sample_prices)
    
    # 결과 출력
    if analysis.get('summary'):
        summary = analysis['summary']
        print(f"\n🎯 종합 판단:")
        print(f"  추천: {summary['recommendation']}")
        print(f"  점수: {summary['overall_score']:.2f}/1.00")
        print(f"  신뢰도: {summary['confidence']:.1%}")
        
        if summary['key_factors']:
            print(f"\n✅ 주요 긍정 요인:")
            for factor in summary['key_factors']:
                print(f"  • {factor}")
        
        if summary['opportunities']:
            print(f"\n🚀 기회 요인:")
            for opp in summary['opportunities']:
                print(f"  • {opp}")
        
        if summary['risks']:
            print(f"\n⚠️ 위험 요인:")
            for risk in summary['risks']:
                print(f"  • {risk}")
    
    # 시장 전체 개요
    print(f"\n🌍 전체 시장 개요:")
    market_overview = analyzer.get_market_overview(["bitcoin", "ethereum"])
    
    if market_overview.get('market_summary'):
        print(market_overview['market_summary'])

if __name__ == "__main__":
    demo_comprehensive_analysis()