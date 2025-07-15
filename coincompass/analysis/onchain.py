"""
온체인 지표 분석 모듈
블록체인 네트워크 데이터 수집 및 분석
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
import json

from ..core.models import MarketSentiment
from ..utils.logger import get_logger
from ..config.settings import Settings

logger = get_logger(__name__)

class OnChainAnalyzer:
    """온체인 데이터 분석기"""
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.apis = {
            'blockstream': 'https://blockstream.info/api',
            'etherscan': 'https://api.etherscan.io/api',
            'btc_explorer': 'https://api.blockchain.info',
            'alternative': 'https://api.alternative.me'
        }
        
    def get_bitcoin_network_stats(self) -> Optional[Dict]:
        """비트코인 네트워크 통계"""
        try:
            # 최신 블록 정보
            response = requests.get(f"{self.apis['blockstream']}/blocks/tip/height", timeout=10)
            latest_height = response.json()
            
            # 최근 블록들 조회
            response = requests.get(f"{self.apis['blockstream']}/blocks", timeout=10)
            blocks = response.json()
            
            # 해시율 계산 (최근 144블록 기준)
            if len(blocks) >= 2:
                block_times = []
                for i in range(min(10, len(blocks)-1)):
                    time_diff = blocks[i]['timestamp'] - blocks[i+1]['timestamp']
                    block_times.append(time_diff)
                
                avg_block_time = sum(block_times) / len(block_times) if block_times else 600
                
                stats = {
                    'latest_block_height': latest_height,
                    'avg_block_time_seconds': avg_block_time,
                    'network_difficulty': blocks[0].get('difficulty') if blocks else None,
                    'total_blocks_24h': 144,  # 예상값
                    'timestamp': datetime.now().isoformat()
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"비트코인 네트워크 통계 수집 오류: {str(e)}")
            
        return None
    
    def get_ethereum_network_stats(self, api_key: Optional[str] = None) -> Optional[Dict]:
        """이더리움 네트워크 통계"""
        if not api_key:
            logger.warning("Etherscan API 키가 필요합니다")
            return None
            
        try:
            # 최신 블록 번호
            params = {
                'module': 'proxy',
                'action': 'eth_blockNumber',
                'apikey': api_key
            }
            response = requests.get(self.apis['etherscan'], params=params, timeout=10)
            block_data = response.json()
            
            if 'result' in block_data:
                latest_block = int(block_data['result'], 16)
                
                # 가스 가격 조회
                gas_params = {
                    'module': 'gastracker',
                    'action': 'gasoracle',
                    'apikey': api_key
                }
                gas_response = requests.get(self.apis['etherscan'], params=gas_params, timeout=10)
                gas_data = gas_response.json()
                
                stats = {
                    'latest_block': latest_block,
                    'safe_gas_price': gas_data.get('result', {}).get('SafeGasPrice'),
                    'standard_gas_price': gas_data.get('result', {}).get('StandardGasPrice'),
                    'fast_gas_price': gas_data.get('result', {}).get('FastGasPrice'),
                    'timestamp': datetime.now().isoformat()
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"이더리움 네트워크 통계 수집 오류: {str(e)}")
            
        return None
    
    def get_blockchain_metrics(self) -> Dict[str, Any]:
        """종합 블록체인 메트릭스"""
        metrics = {
            'bitcoin': None,
            'ethereum': None,
            'collection_timestamp': datetime.now().isoformat()
        }
        
        # 비트코인 메트릭스
        btc_stats = self.get_bitcoin_network_stats()
        if btc_stats:
            metrics['bitcoin'] = btc_stats
            logger.info("✅ 비트코인 온체인 데이터 수집 완료")
        
        # 이더리움 메트릭스 (API 키가 있는 경우)
        eth_api_key = getattr(self.settings.api, 'etherscan_api_key', None)
        if eth_api_key:
            eth_stats = self.get_ethereum_network_stats(eth_api_key)
            if eth_stats:
                metrics['ethereum'] = eth_stats
                logger.info("✅ 이더리움 온체인 데이터 수집 완료")
        else:
            logger.info("ℹ️ Etherscan API 키가 없어 이더리움 데이터 수집 건너뜀")
        
        return metrics
    
    def analyze_network_health(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """네트워크 건강도 분석"""
        analysis = {}
        
        # 비트코인 분석
        if metrics.get('bitcoin'):
            btc = metrics['bitcoin']
            avg_time = btc.get('avg_block_time_seconds', 600)
            
            if avg_time < 300:  # 5분 미만
                analysis['bitcoin_block_time'] = "빠름 (네트워크 활발)"
            elif avg_time > 900:  # 15분 초과
                analysis['bitcoin_block_time'] = "느림 (네트워크 혼잡 가능)"
            else:
                analysis['bitcoin_block_time'] = "정상"
        
        # 이더리움 분석
        if metrics.get('ethereum'):
            eth = metrics['ethereum']
            fast_gas = eth.get('fast_gas_price')
            
            if fast_gas:
                try:
                    gas_price = float(fast_gas)
                    if gas_price < 20:
                        analysis['ethereum_gas'] = "낮음 (트랜잭션 저렴)"
                    elif gas_price > 100:
                        analysis['ethereum_gas'] = "높음 (네트워크 혼잡)"
                    else:
                        analysis['ethereum_gas'] = "보통"
                except ValueError:
                    analysis['ethereum_gas'] = "데이터 오류"
        
        return analysis

class SentimentAnalyzer:
    """센티먼트 분석기"""
    
    def __init__(self):
        self.apis = {
            'fear_greed': 'https://api.alternative.me/fng/',
            'reddit': 'https://www.reddit.com/r/cryptocurrency.json'
        }
    
    def get_fear_greed_index(self) -> Optional[Dict]:
        """공포탐욕지수 조회"""
        try:
            response = requests.get(self.apis['fear_greed'], timeout=10)
            data = response.json()
            
            if 'data' in data and data['data']:
                latest = data['data'][0]
                return {
                    'value': int(latest['value']),
                    'classification': latest['value_classification'],
                    'timestamp': latest['timestamp'],
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"공포탐욕지수 수집 오류: {str(e)}")
            
        return None
    
    def get_reddit_sentiment(self) -> Optional[Dict]:
        """Reddit 센티먼트 분석"""
        try:
            headers = {'User-Agent': 'CoinCompass/1.0'}
            response = requests.get(self.apis['reddit'], headers=headers, timeout=10)
            data = response.json()
            
            posts = data['data']['children']
            
            # 간단한 감정 분석 (키워드 기반)
            positive_keywords = ['bull', 'moon', 'pump', 'buy', 'hodl', 'gain']
            negative_keywords = ['bear', 'dump', 'crash', 'sell', 'loss', 'down']
            
            positive_count = 0
            negative_count = 0
            total_posts = len(posts)
            
            for post in posts:
                title = post['data']['title'].lower()
                for keyword in positive_keywords:
                    if keyword in title:
                        positive_count += 1
                        break
                for keyword in negative_keywords:
                    if keyword in title:
                        negative_count += 1
                        break
            
            # 감정 스코어 계산 (-1 ~ 1)
            if total_posts > 0:
                sentiment_score = (positive_count - negative_count) / total_posts
            else:
                sentiment_score = 0
            
            return {
                'total_posts': total_posts,
                'positive_posts': positive_count,
                'negative_posts': negative_count,
                'sentiment_score': sentiment_score,
                'sentiment_label': self._get_sentiment_label(sentiment_score),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Reddit 센티먼트 수집 오류: {str(e)}")
            
        return None
    
    def _get_sentiment_label(self, score: float) -> str:
        """감정 스코어를 라벨로 변환"""
        if score > 0.1:
            return "긍정적"
        elif score < -0.1:
            return "부정적"
        else:
            return "중립적"
    
    def get_comprehensive_sentiment(self) -> MarketSentiment:
        """종합 센티먼트 분석"""
        fear_greed = self.get_fear_greed_index()
        reddit_data = self.get_reddit_sentiment()
        
        sentiment = MarketSentiment()
        
        if fear_greed:
            sentiment.fear_greed_index = fear_greed['value']
            logger.info(f"📊 공포탐욕지수: {fear_greed['value']} ({fear_greed['classification']})")
        
        if reddit_data:
            sentiment.social_sentiment = reddit_data['sentiment_score']
            logger.info(f"🗣️ Reddit 센티먼트: {reddit_data['sentiment_label']} ({reddit_data['sentiment_score']:.2f})")
        
        return sentiment

def demo_onchain_analysis():
    """온체인 분석 데모"""
    print("🔗 온체인 분석 데모")
    print("="*50)
    
    # 온체인 분석
    onchain = OnChainAnalyzer()
    
    print("📊 블록체인 메트릭스 수집 중...")
    metrics = onchain.get_blockchain_metrics()
    
    if metrics['bitcoin']:
        btc = metrics['bitcoin']
        print(f"🟠 비트코인:")
        print(f"  최신 블록: {btc['latest_block_height']}")
        print(f"  평균 블록시간: {btc['avg_block_time_seconds']:.1f}초")
    
    if metrics['ethereum']:
        eth = metrics['ethereum']
        print(f"🔷 이더리움:")
        print(f"  최신 블록: {eth['latest_block']}")
        print(f"  Fast Gas: {eth['fast_gas_price']} Gwei")
    
    # 네트워크 건강도 분석
    health = onchain.analyze_network_health(metrics)
    if health:
        print(f"\n🏥 네트워크 건강도:")
        for network, status in health.items():
            print(f"  {network}: {status}")
    
    # 센티먼트 분석
    print(f"\n😰 센티먼트 분석:")
    sentiment_analyzer = SentimentAnalyzer()
    sentiment = sentiment_analyzer.get_comprehensive_sentiment()
    
    if sentiment.fear_greed_index:
        print(f"  공포탐욕지수: {sentiment.fear_greed_index}")
    
    if sentiment.social_sentiment:
        print(f"  소셜 센티먼트: {sentiment.social_sentiment:.2f}")

if __name__ == "__main__":
    demo_onchain_analysis()