"""
코인가격에 영향을 주는 요소들과 수집방법
연구 기반의 종합적인 가격 예측 요소 분석
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class PriceInfluenceAnalyzer:
    """가격 영향 요소 분석기"""
    
    def __init__(self):
        self.factors = {
            'technical': [],
            'on_chain': [],
            'macroeconomic': [],
            'sentiment': [],
            'fundamental': []
        }
        
    def get_factor_categories(self):
        """가격 영향 요소 카테고리별 분류"""
        return {
            # 1. 기술적 지표 (Technical Indicators)
            'technical': {
                'price_action': [
                    'RSI (Relative Strength Index)',
                    'MACD (Moving Average Convergence Divergence)',
                    '볼린저 밴드 (Bollinger Bands)',
                    '이동평균선 (Moving Averages)',
                    '피보나치 되돌림',
                    '지지/저항 레벨',
                    '거래량 지표'
                ],
                'volume_indicators': [
                    'On-Balance Volume (OBV)',
                    'Volume Price Trend (VPT)',
                    'Accumulation/Distribution Line',
                    'Chaikin Money Flow',
                    '거래량 가중 평균 가격 (VWAP)'
                ]
            },
            
            # 2. 온체인 지표 (On-Chain Metrics)
            'on_chain': {
                'network_activity': [
                    '활성 주소 수 (Active Addresses)',
                    '거래 건수 (Transaction Count)',
                    '네트워크 해시율 (Hash Rate)',
                    '난이도 조정 (Difficulty Adjustment)',
                    '블록 생성 시간'
                ],
                'holder_behavior': [
                    'HODL 웨이브 (HODL Waves)',
                    '장기/단기 보유자 비율',
                    '고래 활동 (Whale Activity)',
                    '거래소 유입/유출량',
                    'UTXO 연령 분포'
                ],
                'supply_metrics': [
                    '유통 공급량 (Circulating Supply)',
                    '소각량 (Burned Tokens)',
                    '스테이킹량 (Staked Amount)',
                    '락업 물량 (Locked Tokens)',
                    '인플레이션/디플레이션율'
                ],
                'market_metrics': [
                    'MVRV 비율 (Market Value to Realized Value)',
                    'NVT 비율 (Network Value to Transactions)',
                    'Puell Multiple',
                    'Stock-to-Flow 모델',
                    '실현 가격 (Realized Price)'
                ]
            },
            
            # 3. 거시경제 지표 (Macroeconomic Indicators)
            'macroeconomic': {
                'monetary_policy': [
                    '연방기금금리 (Federal Funds Rate)',
                    '인플레이션율 (CPI, PPI)',
                    '양적 완화 정책',
                    '통화 공급량 (M1, M2)',
                    '달러 지수 (DXY)'
                ],
                'economic_indicators': [
                    'GDP 성장률',
                    '실업률 (Unemployment Rate)',
                    '소비자 신뢰지수',
                    '선행 경제지표',
                    '국가 부채 수준'
                ],
                'market_conditions': [
                    'VIX 지수 (공포지수)',
                    '주식시장 지수 (S&P 500, NASDAQ)',
                    '금/은 가격',
                    '유가 (Oil Prices)',
                    '환율 변동'
                ]
            },
            
            # 4. 센티먼트 지표 (Sentiment Indicators)
            'sentiment': {
                'social_media': [
                    '트위터 언급량 및 감정',
                    '레딧 토론 활성도',
                    '텔레그램 그룹 활동',
                    '유튜브 언급량',
                    '구글 검색 트렌드'
                ],
                'market_sentiment': [
                    'Fear & Greed Index',
                    '펀딩 비율 (Funding Rate)',
                    '옵션 Put/Call 비율',
                    '선물 미결제약정',
                    'Long/Short 비율'
                ],
                'news_analysis': [
                    '뉴스 기사 감정 분석',
                    '규제 뉴스 빈도',
                    '기관 투자 뉴스',
                    '개발 관련 뉴스',
                    '파트너십 발표'
                ]
            },
            
            # 5. 펀더멘털 요소 (Fundamental Factors)
            'fundamental': {
                'project_metrics': [
                    '개발자 활동 (GitHub 커밋)',
                    '네트워크 업그레이드',
                    '파트너십 체결',
                    '실제 사용사례 (DApp 사용량)',
                    '생태계 성장'
                ],
                'regulatory': [
                    '정부 규제 정책',
                    'ETF 승인/거부',
                    '거래소 상장/상폐',
                    '세금 정책',
                    '법적 분류 변화'
                ],
                'institutional': [
                    '기관 투자자 유입',
                    '기업 비트코인 보유',
                    '헤지펀드 포지션',
                    '보험/연금 기금 투자',
                    '은행 서비스 도입'
                ]
            }
        }

class OnChainDataCollector:
    """온체인 데이터 수집기"""
    
    def __init__(self):
        self.apis = {
            'etherscan': 'https://api.etherscan.io/api',
            'blockchair': 'https://api.blockchair.com',
            'btc_explorer': 'https://blockstream.info/api',
            'glassnode': 'https://api.glassnode.com'
        }
    
    def get_btc_network_stats(self):
        """비트코인 네트워크 통계 (무료)"""
        try:
            # Blockstream API (무료)
            response = requests.get(f"{self.apis['btc_explorer']}/blocks/tip/height")
            latest_height = response.json()
            
            # 해시율 정보
            response = requests.get(f"{self.apis['btc_explorer']}/blocks")
            blocks = response.json()
            
            return {
                'latest_block': latest_height,
                'recent_blocks': len(blocks),
                'avg_block_time': self._calculate_avg_block_time(blocks)
            }
        except Exception as e:
            print(f"비트코인 네트워크 데이터 수집 오류: {e}")
            return None
    
    def get_eth_network_stats(self, api_key=None):
        """이더리움 네트워크 통계"""
        if not api_key:
            print("Etherscan API 키가 필요합니다 (무료 등록)")
            return None
            
        try:
            # 최신 블록 정보
            params = {
                'module': 'proxy',
                'action': 'eth_blockNumber',
                'apikey': api_key
            }
            response = requests.get(self.apis['etherscan'], params=params)
            block_data = response.json()
            
            return {
                'latest_block': int(block_data['result'], 16),
                'source': 'Etherscan'
            }
        except Exception as e:
            print(f"이더리움 네트워크 데이터 수집 오류: {e}")
            return None
    
    def _calculate_avg_block_time(self, blocks):
        """평균 블록 생성 시간 계산"""
        if len(blocks) < 2:
            return None
        
        timestamps = [block['timestamp'] for block in blocks]
        time_diffs = [timestamps[i-1] - timestamps[i] for i in range(1, len(timestamps))]
        return sum(time_diffs) / len(time_diffs) if time_diffs else None

class MacroeconomicDataCollector:
    """거시경제 데이터 수집기"""
    
    def __init__(self):
        self.free_apis = {
            'fed': 'https://api.stlouisfed.org/fred/series/observations',
            'yahoo_finance': 'https://query1.finance.yahoo.com/v8/finance/chart',
            'fmp': 'https://financialmodelingprep.com/api/v3'
        }
    
    def get_fed_data(self, series_id, api_key=None):
        """연준 데이터 조회 (FRED API)"""
        if not api_key:
            print("FRED API 키가 필요합니다 (무료 등록)")
            return None
            
        try:
            params = {
                'series_id': series_id,
                'api_key': api_key,
                'file_type': 'json'
            }
            response = requests.get(self.free_apis['fed'], params=params)
            return response.json()
        except Exception as e:
            print(f"FRED 데이터 수집 오류: {e}")
            return None
    
    def get_market_indices(self):
        """주요 시장 지수 조회 (Yahoo Finance - 무료)"""
        indices = {
            'SPY': 'S&P 500',
            'QQQ': 'NASDAQ-100',
            'GLD': 'Gold',
            'DXY': 'Dollar Index',
            'VIX': 'Volatility Index'
        }
        
        results = {}
        for symbol, name in indices.items():
            try:
                url = f"{self.free_apis['yahoo_finance']}/{symbol}"
                response = requests.get(url)
                data = response.json()
                
                if 'chart' in data and data['chart']['result']:
                    price = data['chart']['result'][0]['meta']['regularMarketPrice']
                    results[symbol] = {
                        'name': name,
                        'price': price,
                        'source': 'Yahoo Finance'
                    }
            except Exception as e:
                print(f"{symbol} 데이터 수집 오류: {e}")
        
        return results

class SentimentDataCollector:
    """센티먼트 데이터 수집기"""
    
    def __init__(self):
        self.apis = {
            'fear_greed': 'https://api.alternative.me/fng/',
            'reddit': 'https://www.reddit.com/r/cryptocurrency.json',
            'google_trends': 'https://trends.google.com'  # 비공식
        }
    
    def get_fear_greed_index(self):
        """공포 탐욕 지수 조회 (무료)"""
        try:
            response = requests.get(self.apis['fear_greed'])
            data = response.json()
            
            if 'data' in data and data['data']:
                latest = data['data'][0]
                return {
                    'value': int(latest['value']),
                    'classification': latest['value_classification'],
                    'timestamp': latest['timestamp'],
                    'source': 'Alternative.me'
                }
        except Exception as e:
            print(f"공포 탐욕 지수 수집 오류: {e}")
            return None
    
    def get_reddit_sentiment(self):
        """레딧 암호화폐 커뮤니티 활동도 (무료)"""
        try:
            response = requests.get(self.apis['reddit'], 
                                  headers={'User-Agent': 'CryptoAnalyzer/1.0'})
            data = response.json()
            
            posts = data['data']['children']
            
            return {
                'total_posts': len(posts),
                'hot_posts': [post['data']['title'] for post in posts[:5]],
                'avg_score': np.mean([post['data']['score'] for post in posts]),
                'source': 'Reddit'
            }
        except Exception as e:
            print(f"레딧 데이터 수집 오류: {e}")
            return None

def demonstrate_data_collection():
    """데이터 수집 시연"""
    print("📊 코인가격 영향 요소 데이터 수집 시연")
    
    # 1. 가격 영향 요소 분류 출력
    analyzer = PriceInfluenceAnalyzer()
    factors = analyzer.get_factor_categories()
    
    print("\n🔍 주요 가격 영향 요소들:")
    for category, subcategories in factors.items():
        print(f"\n{category.upper()}:")
        for subcat, items in subcategories.items():
            print(f"  {subcat}:")
            for item in items[:3]:  # 처음 3개만 표시
                print(f"    - {item}")
    
    # 2. 온체인 데이터 수집 테스트
    print("\n🔗 온체인 데이터 수집 테스트:")
    onchain = OnChainDataCollector()
    
    btc_stats = onchain.get_btc_network_stats()
    if btc_stats:
        print(f"  BTC 최신 블록: {btc_stats['latest_block']}")
        if btc_stats['avg_block_time']:
            print(f"  평균 블록 시간: {btc_stats['avg_block_time']:.1f}초")
    
    # 3. 거시경제 데이터 수집 테스트
    print("\n📈 거시경제 데이터 수집 테스트:")
    macro = MacroeconomicDataCollector()
    
    indices = macro.get_market_indices()
    for symbol, data in indices.items():
        print(f"  {data['name']}: ${data['price']:.2f}")
    
    # 4. 센티먼트 데이터 수집 테스트
    print("\n😰 센티먼트 데이터 수집 테스트:")
    sentiment = SentimentDataCollector()
    
    fear_greed = sentiment.get_fear_greed_index()
    if fear_greed:
        print(f"  공포탐욕지수: {fear_greed['value']} ({fear_greed['classification']})")
    
    reddit_data = sentiment.get_reddit_sentiment()
    if reddit_data:
        print(f"  레딧 활동: {reddit_data['total_posts']}개 포스트")
        print(f"  평균 점수: {reddit_data['avg_score']:.1f}")

def create_data_collection_summary():
    """데이터 수집 방법 요약"""
    summary = """
🎯 코인가격 영향 요소 및 데이터 수집 방법 요약

1️⃣ 기술적 지표 (Technical Indicators)
   📊 데이터 소스: 거래소 API (Binance, CoinGecko, CoinPaprika)
   🔄 업데이트: 실시간 ~ 1분
   💰 비용: 무료 (제한적) / 유료 (고급)

2️⃣ 온체인 지표 (On-Chain Metrics)
   📊 데이터 소스: 
   - Bitcoin: Blockstream API (무료)
   - Ethereum: Etherscan API (무료/유료)
   - 다중체인: Blockchair API (무료/유료)
   - 고급 분석: Glassnode, CryptoQuant (유료)
   🔄 업데이트: 블록 생성시 (10분-15초)
   💰 비용: 기본 무료, 고급 유료

3️⃣ 거시경제 지표 (Macroeconomic)
   📊 데이터 소스:
   - FRED API (연준 데이터, 무료)
   - Yahoo Finance API (시장 지수, 무료)
   - Alpha Vantage (경제 지표, 무료/유료)
   🔄 업데이트: 일/주/월 단위
   💰 비용: 대부분 무료

4️⃣ 센티먼트 지표 (Sentiment)
   📊 데이터 소스:
   - Alternative.me (공포탐욕지수, 무료)
   - Reddit API (커뮤니티 활동, 무료)
   - Twitter API (소셜 센티먼트, 유료)
   - Google Trends (검색 관심도, 무료)
   🔄 업데이트: 실시간 ~ 일 단위
   💰 비용: 혼합 (무료/유료)

5️⃣ 펀더멘털 요소 (Fundamental)
   📊 데이터 소스:
   - GitHub API (개발 활동, 무료)
   - 뉴스 API (규제/개발 뉴스, 무료/유료)
   - DeFiPulse (DeFi 지표, 무료/유료)
   🔄 업데이트: 실시간 ~ 주 단위
   💰 비용: 혼합 (무료/유료)

💡 권장 무료 시작 조합:
- 가격: CoinPaprika API
- 온체인: Blockstream + Etherscan
- 거시경제: FRED + Yahoo Finance  
- 센티먼트: Alternative.me + Reddit
- 펀더멘털: GitHub API + 뉴스 스크래핑
"""
    
    return summary

if __name__ == "__main__":
    demonstrate_data_collection()
    print(create_data_collection_summary())