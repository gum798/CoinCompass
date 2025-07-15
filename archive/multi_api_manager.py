"""
다중 API 관리자 - 여러 무료 API를 돌아가면서 사용
CoinPaprika, CoinGecko, CoinMarketCap 로테이션 및 fallback
"""

import requests
import pandas as pd
import time
import json
from datetime import datetime, timedelta
import random

class APIProvider:
    """API 제공자 기본 클래스"""
    
    def __init__(self, name, base_url, rate_limit_per_minute=60, requires_key=False):
        self.name = name
        self.base_url = base_url
        self.rate_limit_per_minute = rate_limit_per_minute
        self.requires_key = requires_key
        self.request_times = []
        self.last_error_time = None
        self.error_count = 0
        self.is_available = True
        
    def can_make_request(self):
        """요청 가능 여부 확인 (레이트 리미트 체크)"""
        now = datetime.now()
        
        # 1분 이내의 요청만 유지
        self.request_times = [t for t in self.request_times if (now - t).seconds < 60]
        
        # 레이트 리미트 체크
        if len(self.request_times) >= self.rate_limit_per_minute:
            return False
            
        # 최근 에러 발생시 잠시 대기
        if self.last_error_time and (now - self.last_error_time).seconds < 30:
            return False
            
        return self.is_available
    
    def record_request(self):
        """요청 기록"""
        self.request_times.append(datetime.now())
    
    def record_error(self):
        """에러 기록"""
        self.error_count += 1
        self.last_error_time = datetime.now()
        
        # 에러가 3번 이상 발생하면 일시적으로 비활성화
        if self.error_count >= 3:
            self.is_available = False
            print(f"⚠️ {self.name} API 일시적 비활성화 (에러 {self.error_count}회)")
    
    def reset_errors(self):
        """에러 카운트 리셋"""
        self.error_count = 0
        self.is_available = True
        self.last_error_time = None

class CoinPaprikaProvider(APIProvider):
    """CoinPaprika API 제공자"""
    
    def __init__(self):
        super().__init__("CoinPaprika", "https://api.coinpaprika.com/v1", 
                        rate_limit_per_minute=50, requires_key=False)
        self.coin_id_map = {
            'bitcoin': 'btc-bitcoin',
            'ethereum': 'eth-ethereum', 
            'ripple': 'xrp-xrp',
            'binancecoin': 'bnb-binance-coin',
            'solana': 'sol-solana',
            'dogecoin': 'doge-dogecoin',
            'tron': 'trx-tron',
            'usd-coin': 'usdc-usd-coin',
            'tether': 'usdt-tether',
            'staked-ether': 'steth-lido-staked-ether'
        }
    
    def get_price(self, coin_id):
        """가격 조회"""
        if not self.can_make_request():
            return None
            
        try:
            paprika_id = self.coin_id_map.get(coin_id, coin_id)
            response = requests.get(f"{self.base_url}/tickers/{paprika_id}", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.record_request()
            
            return {
                'price': data['quotes']['USD']['price'],
                'market_cap': data['quotes']['USD']['market_cap'],
                'volume_24h': data['quotes']['USD']['volume_24h'],
                'price_change_24h': data['quotes']['USD']['percent_change_24h'],
                'source': self.name
            }
            
        except Exception as e:
            self.record_error()
            print(f"❌ {self.name} 오류: {str(e)}")
            return None
    
    def get_top_coins(self, limit=10):
        """상위 코인 목록"""
        if not self.can_make_request():
            return None
            
        try:
            response = requests.get(f"{self.base_url}/tickers", 
                                  params={'limit': limit}, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.record_request()
            
            coins = []
            for coin in data:
                if coin['quotes']['USD']['price']:
                    coins.append({
                        'id': coin['id'],
                        'symbol': coin['symbol'],
                        'name': coin['name'],
                        'current_price': coin['quotes']['USD']['price'],
                        'market_cap': coin['quotes']['USD']['market_cap'],
                        'total_volume': coin['quotes']['USD']['volume_24h'],
                        'price_change_percentage_24h': coin['quotes']['USD']['percent_change_24h']
                    })
            
            return pd.DataFrame(coins)
            
        except Exception as e:
            self.record_error()
            print(f"❌ {self.name} 상위 코인 조회 오류: {str(e)}")
            return None

class CoinGeckoProvider(APIProvider):
    """CoinGecko API 제공자"""
    
    def __init__(self):
        super().__init__("CoinGecko", "https://api.coingecko.com/api/v3", 
                        rate_limit_per_minute=30, requires_key=False)
    
    def get_price(self, coin_id):
        """가격 조회"""
        if not self.can_make_request():
            return None
            
        try:
            response = requests.get(f"{self.base_url}/simple/price", 
                                  params={
                                      'ids': coin_id,
                                      'vs_currencies': 'usd',
                                      'include_24hr_change': 'true',
                                      'include_market_cap': 'true',
                                      'include_24hr_vol': 'true'
                                  }, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.record_request()
            
            if coin_id in data:
                coin_data = data[coin_id]
                return {
                    'price': coin_data['usd'],
                    'market_cap': coin_data.get('usd_market_cap', 0),
                    'volume_24h': coin_data.get('usd_24h_vol', 0),
                    'price_change_24h': coin_data.get('usd_24h_change', 0),
                    'source': self.name
                }
            
            return None
            
        except Exception as e:
            self.record_error()
            print(f"❌ {self.name} 오류: {str(e)}")
            return None
    
    def get_top_coins(self, limit=10):
        """상위 코인 목록"""
        if not self.can_make_request():
            return None
            
        try:
            response = requests.get(f"{self.base_url}/coins/markets",
                                  params={
                                      'vs_currency': 'usd',
                                      'order': 'market_cap_desc',
                                      'per_page': limit,
                                      'page': 1,
                                      'sparkline': 'false'
                                  }, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.record_request()
            
            df = pd.DataFrame(data)
            return df[['id', 'symbol', 'name', 'current_price', 'market_cap', 
                      'total_volume', 'price_change_percentage_24h']]
            
        except Exception as e:
            self.record_error()
            print(f"❌ {self.name} 상위 코인 조회 오류: {str(e)}")
            return None

class MultiAPIManager:
    """다중 API 관리자"""
    
    def __init__(self):
        self.providers = [
            CoinPaprikaProvider(),
            CoinGeckoProvider()
        ]
        self.current_provider_index = 0
        self.request_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'provider_usage': {}
        }
        
    def get_next_available_provider(self):
        """사용 가능한 다음 제공자 찾기"""
        attempts = 0
        while attempts < len(self.providers):
            provider = self.providers[self.current_provider_index]
            
            if provider.can_make_request():
                return provider
            
            # 다음 제공자로 이동
            self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
            attempts += 1
        
        return None
    
    def get_price_with_fallback(self, coin_id):
        """여러 API를 시도하여 가격 조회"""
        self.request_stats['total_requests'] += 1
        
        # 모든 제공자 시도
        for _ in range(len(self.providers)):
            provider = self.get_next_available_provider()
            
            if provider is None:
                # 모든 제공자가 사용 불가능
                print("⚠️ 모든 API 제공자가 일시적으로 사용 불가능합니다.")
                time.sleep(5)  # 5초 대기 후 재시도
                continue
            
            print(f"🔄 {provider.name} API 사용 중...")
            result = provider.get_price(coin_id)
            
            if result:
                self.request_stats['successful_requests'] += 1
                self.request_stats['provider_usage'][provider.name] = \
                    self.request_stats['provider_usage'].get(provider.name, 0) + 1
                
                # 다음 요청을 위해 제공자 순환
                self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
                
                return result
            
            # 실패시 다음 제공자로
            self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
        
        self.request_stats['failed_requests'] += 1
        return None
    
    def get_top_coins_with_fallback(self, limit=10):
        """여러 API를 시도하여 상위 코인 조회"""
        for _ in range(len(self.providers)):
            provider = self.get_next_available_provider()
            
            if provider is None:
                continue
            
            print(f"📊 {provider.name}에서 상위 {limit}개 코인 조회 중...")
            result = provider.get_top_coins(limit)
            
            if result is not None:
                self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
                return result
            
            self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
        
        return None
    
    def get_multiple_prices(self, coins, delay=1.5):
        """여러 코인의 가격을 순차적으로 조회"""
        results = {}
        
        for coin in coins:
            print(f"💰 {coin} 가격 조회 중...")
            price_data = self.get_price_with_fallback(coin)
            
            if price_data:
                results[coin] = price_data
                print(f"  ✅ ${price_data['price']:,.2f} (출처: {price_data['source']})")
            else:
                print(f"  ❌ 가격 조회 실패")
            
            # API 제한 방지를 위한 대기
            if len(coins) > 1:  # 여러 코인 조회시에만 대기
                time.sleep(delay)
        
        return results
    
    def reset_all_providers(self):
        """모든 제공자의 에러 카운트 리셋"""
        for provider in self.providers:
            provider.reset_errors()
        print("🔄 모든 API 제공자 상태를 리셋했습니다.")
    
    def get_stats(self):
        """요청 통계 조회"""
        return self.request_stats.copy()
    
    def print_stats(self):
        """통계 출력"""
        stats = self.get_stats()
        success_rate = (stats['successful_requests'] / max(stats['total_requests'], 1)) * 100
        
        print(f"\n📊 API 사용 통계:")
        print(f"총 요청: {stats['total_requests']}")
        print(f"성공: {stats['successful_requests']}")
        print(f"실패: {stats['failed_requests']}")
        print(f"성공률: {success_rate:.1f}%")
        
        if stats['provider_usage']:
            print(f"제공자별 사용량:")
            for provider, count in stats['provider_usage'].items():
                print(f"  - {provider}: {count}회")

def test_multi_api():
    """다중 API 시스템 테스트"""
    print("🧪 다중 API 시스템 테스트 시작...")
    
    manager = MultiAPIManager()
    
    # 1. 개별 코인 테스트
    print("\n1. 개별 코인 가격 조회 테스트")
    btc_data = manager.get_price_with_fallback('bitcoin')
    if btc_data:
        print(f"✅ Bitcoin: ${btc_data['price']:,.2f} (출처: {btc_data['source']})")
    
    # 2. 여러 코인 테스트
    print("\n2. 여러 코인 가격 조회 테스트")
    coins = ['bitcoin', 'ethereum', 'ripple']
    results = manager.get_multiple_prices(coins)
    
    # 3. 상위 코인 테스트
    print("\n3. 상위 10개 코인 조회 테스트")
    top_coins = manager.get_top_coins_with_fallback(10)
    if top_coins is not None:
        print(f"✅ 상위 {len(top_coins)}개 코인 조회 성공")
        print(top_coins[['name', 'current_price', 'price_change_percentage_24h']].head())
    
    # 4. 통계 출력
    manager.print_stats()

if __name__ == "__main__":
    test_multi_api()