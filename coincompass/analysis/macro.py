"""
거시경제 지표 분석 모듈
경제 데이터 수집 및 암호화폐 시장과의 상관관계 분석
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import yfinance as yf
import urllib3

# SSL 경고 억제
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from ..utils.logger import get_logger
from ..config.settings import Settings
from ..config.api_keys import get_api_key_manager

logger = get_logger(__name__)

class MacroeconomicAnalyzer:
    """거시경제 분석기"""
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.api_key_manager = get_api_key_manager()
        self.apis = {
            'fred': 'https://api.stlouisfed.org/fred/series/observations',
            'yahoo': 'https://query1.finance.yahoo.com/v8/finance/chart',
            'treasury': 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service'
        }
        
        # 주요 경제 지표 시리즈 ID (FRED)
        self.fred_series = {
            'fed_rate': 'FEDFUNDS',              # 연방기금금리
            'cpi': 'CPIAUCSL',                   # 소비자물가지수
            'unemployment': 'UNRATE',            # 실업률
            'gdp': 'GDP',                        # GDP
            'dxy': 'DTWEXBGS',                   # 달러지수 (주간)
            'm2': 'M2SL',                        # 통화공급량 M2
            '10y_yield': 'GS10',                 # 10년 국채 수익률
            'vix': 'VIXCLS'                      # VIX 지수
        }
        
        # 주요 시장 지수
        self.market_symbols = {
            'SP500': '^GSPC',
            'NASDAQ': '^IXIC',
            'DOW': '^DJI',
            'GOLD': 'GC=F',
            'OIL': 'CL=F',
            'DXY': 'DX-Y.NYB',
            'VIX': '^VIX',
            'TREASURY_10Y': '^TNX'
        }
    
    def get_fred_data(self, series_id: str, api_key: Optional[str] = None, 
                      days_back: int = 30) -> Optional[Dict]:
        """FRED API에서 경제 데이터 조회"""
        if not api_key:
            logger.warning("FRED API 키가 필요합니다 (https://fred.stlouisfed.org/docs/api/api_key.html)")
            return None
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            params = {
                'series_id': series_id,
                'api_key': api_key,
                'file_type': 'json',
                'observation_start': start_date.strftime('%Y-%m-%d'),
                'observation_end': end_date.strftime('%Y-%m-%d'),
                'sort_order': 'desc',
                'limit': 1
            }
            
            response = requests.get(self.apis['fred'], params=params, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()
            
            if 'observations' in data and data['observations']:
                latest = data['observations'][0]
                if latest['value'] != '.':  # FRED에서 결측값은 '.'으로 표시
                    return {
                        'value': float(latest['value']),
                        'date': latest['date'],
                        'series_id': series_id,
                        'last_updated': datetime.now().isoformat()
                    }
            
        except Exception as e:
            logger.error(f"FRED 데이터 수집 오류 ({series_id}): {str(e)}")
        
        return None
    
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """Yahoo Finance에서 시장 데이터 조회"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if not hist.empty:
                latest = hist.iloc[-1]
                prev = hist.iloc[-2] if len(hist) > 1 else latest
                
                change = ((latest['Close'] - prev['Close']) / prev['Close']) * 100
                
                return {
                    'symbol': symbol,
                    'price': latest['Close'],
                    'volume': latest['Volume'],
                    'change_1d': change,
                    'high_52w': hist['High'].max(),
                    'low_52w': hist['Low'].min(),
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"시장 데이터 수집 오류 ({symbol}): {str(e)}")
        
        return None
    
    def get_economic_indicators(self, fred_api_key: Optional[str] = None) -> Dict[str, Any]:
        """주요 경제 지표 수집"""
        indicators = {}
        
        # FRED API 키 확인 (저장된 키 우선, 매개변수 키 차순위)
        api_key = fred_api_key or self.api_key_manager.load_api_key('fred')
        
        # FRED 데이터 수집
        if api_key:
            logger.info("📊 FRED 경제 지표 수집 중...")
            for name, series_id in self.fred_series.items():
                data = self.get_fred_data(series_id, api_key)
                if data:
                    indicators[name] = data
                    logger.debug(f"✅ {name}: {data['value']}")
        else:
            logger.warning("FRED API 키가 없어 경제 지표 수집을 건너뜁니다")
        
        # 시장 지수 데이터 수집
        logger.info("📈 시장 지수 데이터 수집 중...")
        market_data = {}
        for name, symbol in self.market_symbols.items():
            data = self.get_market_data(symbol)
            if data:
                market_data[name] = data
                logger.debug(f"✅ {name}: ${data['price']:.2f} ({data['change_1d']:+.2f}%)")
        
        if market_data:
            indicators['market_indices'] = market_data
        
        indicators['collection_timestamp'] = datetime.now().isoformat()
        return indicators
    
    def analyze_market_conditions(self, indicators: Dict[str, Any]) -> Dict[str, str]:
        """시장 상황 분석"""
        analysis = {}
        
        # VIX 분석 (공포지수)
        if 'market_indices' in indicators and 'VIX' in indicators['market_indices']:
            vix_data = indicators['market_indices']['VIX']
            vix_level = vix_data['price']
            
            if vix_level < 15:
                analysis['market_fear'] = "낮음 (시장 안정)"
            elif vix_level > 30:
                analysis['market_fear'] = "높음 (시장 불안)"
            else:
                analysis['market_fear'] = "보통"
        
        # 달러 지수 분석
        if 'market_indices' in indicators and 'DXY' in indicators['market_indices']:
            dxy_data = indicators['market_indices']['DXY']
            dxy_change = dxy_data['change_1d']
            
            if dxy_change > 1:
                analysis['dollar_strength'] = "강세 (암호화폐에 부정적)"
            elif dxy_change < -1:
                analysis['dollar_strength'] = "약세 (암호화폐에 긍정적)"
            else:
                analysis['dollar_strength'] = "보합"
        
        # 금 가격 분석
        if 'market_indices' in indicators and 'GOLD' in indicators['market_indices']:
            gold_data = indicators['market_indices']['GOLD']
            gold_change = gold_data['change_1d']
            
            if gold_change > 2:
                analysis['safe_haven_demand'] = "높음 (불확실성 증가)"
            elif gold_change < -2:
                analysis['safe_haven_demand'] = "낮음 (위험 선호)"
            else:
                analysis['safe_haven_demand'] = "보통"
        
        # 10년 국채 수익률 분석
        if 'market_indices' in indicators and 'TREASURY_10Y' in indicators['market_indices']:
            treasury_data = indicators['market_indices']['TREASURY_10Y']
            yield_level = treasury_data['price']
            
            if yield_level > 5:
                analysis['interest_rate_environment'] = "높음 (암호화폐에 부정적)"
            elif yield_level < 2:
                analysis['interest_rate_environment'] = "낮음 (암호화폐에 긍정적)"
            else:
                analysis['interest_rate_environment'] = "보통"
        
        return analysis
    
    def calculate_crypto_correlation_signals(self, indicators: Dict[str, Any]) -> Dict[str, float]:
        """암호화폐와 거시경제 지표의 상관관계 기반 신호"""
        signals = {}
        
        market_data = indicators.get('market_indices', {})
        
        # 나스닥과의 상관관계 (높은 상관관계)
        if 'NASDAQ' in market_data:
            nasdaq_change = market_data['NASDAQ']['change_1d']
            if nasdaq_change > 2:
                signals['tech_stock_momentum'] = 0.7  # 긍정적
            elif nasdaq_change < -2:
                signals['tech_stock_momentum'] = -0.7  # 부정적
            else:
                signals['tech_stock_momentum'] = 0
        
        # 달러 지수와의 역상관관계
        if 'DXY' in market_data:
            dxy_change = market_data['DXY']['change_1d']
            signals['dollar_inverse_correlation'] = -dxy_change / 100  # 역상관
        
        # VIX와의 역상관관계 (위험 회피)
        if 'VIX' in market_data:
            vix_change = market_data['VIX']['change_1d']
            signals['risk_sentiment'] = -vix_change / 100  # 역상관
        
        # 금과의 상관관계 (대안 자산)
        if 'GOLD' in market_data:
            gold_change = market_data['GOLD']['change_1d']
            signals['alternative_asset_flow'] = gold_change / 100
        
        return signals
    
    def generate_macro_summary(self, indicators: Dict[str, Any]) -> str:
        """거시경제 상황 요약"""
        analysis = self.analyze_market_conditions(indicators)
        signals = self.calculate_crypto_correlation_signals(indicators)
        
        summary = "📊 거시경제 상황 요약:\n"
        
        if analysis:
            summary += "\n🔍 주요 지표 분석:\n"
            for indicator, status in analysis.items():
                summary += f"  • {indicator.replace('_', ' ').title()}: {status}\n"
        
        if signals:
            summary += "\n📈 암호화폐 영향 신호:\n"
            for signal_name, value in signals.items():
                direction = "긍정적" if value > 0.3 else "부정적" if value < -0.3 else "중립적"
                summary += f"  • {signal_name.replace('_', ' ').title()}: {direction} ({value:+.2f})\n"
        
        # 종합 점수 계산
        if signals:
            overall_score = sum(signals.values()) / len(signals)
            if overall_score > 0.2:
                overall_sentiment = "암호화폐에 긍정적"
            elif overall_score < -0.2:
                overall_sentiment = "암호화폐에 부정적"
            else:
                overall_sentiment = "중립적"
            
            summary += f"\n🎯 종합 판단: {overall_sentiment} (점수: {overall_score:+.2f})\n"
        
        return summary

def demo_macro_analysis():
    """거시경제 분석 데모"""
    print("📊 거시경제 분석 데모")
    print("="*50)
    
    analyzer = MacroeconomicAnalyzer()
    
    print("📈 경제 지표 수집 중...")
    # FRED API 키 없이 시장 데이터만 수집
    indicators = analyzer.get_economic_indicators()
    
    if indicators.get('market_indices'):
        print("\n💹 주요 시장 지수:")
        for name, data in indicators['market_indices'].items():
            print(f"  {name}: ${data['price']:.2f} ({data['change_1d']:+.2f}%)")
    
    # 시장 상황 분석
    analysis = analyzer.analyze_market_conditions(indicators)
    if analysis:
        print(f"\n🔍 시장 상황 분석:")
        for indicator, status in analysis.items():
            print(f"  {indicator.replace('_', ' ').title()}: {status}")
    
    # 암호화폐 상관관계 신호
    signals = analyzer.calculate_crypto_correlation_signals(indicators)
    if signals:
        print(f"\n📊 암호화폐 영향 신호:")
        for signal_name, value in signals.items():
            direction = "📈" if value > 0 else "📉" if value < 0 else "➡️"
            print(f"  {direction} {signal_name.replace('_', ' ').title()}: {value:+.2f}")
    
    # 종합 요약
    summary = analyzer.generate_macro_summary(indicators)
    print(f"\n{summary}")

if __name__ == "__main__":
    demo_macro_analysis()