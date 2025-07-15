"""
추가 무료 API들을 테스트하는 모듈
CoinPaprika, Finnhub 등 대안 API 연동
"""

import requests
import pandas as pd
import time
from datetime import datetime

class CoinPaprikaAPI:
    """CoinPaprika API 클래스 - API 키 불필요"""
    
    def __init__(self):
        self.base_url = "https://api.coinpaprika.com/v1"
    
    def get_coins_list(self):
        """전체 코인 목록 조회"""
        try:
            response = requests.get(f"{self.base_url}/coins")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"CoinPaprika API 오류: {e}")
            return None
    
    def get_coin_price(self, coin_id="btc-bitcoin"):
        """특정 코인 가격 조회"""
        try:
            response = requests.get(f"{self.base_url}/tickers/{coin_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"CoinPaprika 가격 조회 오류: {e}")
            return None
    
    def get_global_stats(self):
        """글로벌 시장 통계"""
        try:
            response = requests.get(f"{self.base_url}/global")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"CoinPaprika 글로벌 통계 오류: {e}")
            return None

class CryptoCompareAPI:
    """CryptoCompare API 클래스"""
    
    def __init__(self):
        self.base_url = "https://min-api.cryptocompare.com/data"
    
    def get_price(self, fsym="BTC", tsyms="USD"):
        """현재 가격 조회"""
        try:
            response = requests.get(f"{self.base_url}/price", 
                                  params={'fsym': fsym, 'tsyms': tsyms})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"CryptoCompare API 오류: {e}")
            return None
    
    def get_historical_daily(self, fsym="BTC", tsym="USD", limit=30):
        """일별 과거 데이터"""
        try:
            response = requests.get(f"{self.base_url}/v2/histoday",
                                  params={'fsym': fsym, 'tsym': tsym, 'limit': limit})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"CryptoCompare 과거 데이터 오류: {e}")
            return None

class FinnhubAPI:
    """Finnhub API 클래스 (무료 tier)"""
    
    def __init__(self, api_key=None):
        self.base_url = "https://finnhub.io/api/v1"
        self.api_key = api_key  # 무료 등록 필요
    
    def get_crypto_price(self, symbol="BINANCE:BTCUSDT"):
        """암호화폐 가격 조회"""
        if not self.api_key:
            print("Finnhub API 키가 필요합니다 (무료 등록)")
            return None
            
        try:
            response = requests.get(f"{self.base_url}/quote",
                                  params={'symbol': symbol, 'token': self.api_key})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Finnhub API 오류: {e}")
            return None

class MultiAPIManager:
    """여러 API를 조합해서 사용하는 매니저"""
    
    def __init__(self):
        self.coinpaprika = CoinPaprikaAPI()
        self.cryptocompare = CryptoCompareAPI()
        self.current_api = 0  # 로테이션용
        
    def get_price_with_fallback(self, coin="bitcoin"):
        """여러 API를 순차적으로 시도"""
        
        # 1. CoinPaprika 시도
        try:
            if coin == "bitcoin":
                result = self.coinpaprika.get_coin_price("btc-bitcoin")
            elif coin == "ethereum":
                result = self.coinpaprika.get_coin_price("eth-ethereum")
            else:
                result = None
                
            if result:
                return {
                    'source': 'CoinPaprika',
                    'price': result['quotes']['USD']['price'],
                    'change_24h': result['quotes']['USD']['percent_change_24h'],
                    'market_cap': result['quotes']['USD']['market_cap']
                }
        except Exception as e:
            print(f"CoinPaprika 실패: {e}")
        
        # 2. CryptoCompare 시도
        try:
            symbol_map = {'bitcoin': 'BTC', 'ethereum': 'ETH', 'ripple': 'XRP'}
            symbol = symbol_map.get(coin, 'BTC')
            
            result = self.cryptocompare.get_price(symbol)
            if result and 'USD' in result:
                return {
                    'source': 'CryptoCompare',
                    'price': result['USD'],
                    'change_24h': None,
                    'market_cap': None
                }
        except Exception as e:
            print(f"CryptoCompare 실패: {e}")
        
        return None
    
    def get_multiple_prices(self, coins=['bitcoin', 'ethereum', 'ripple']):
        """여러 코인 가격을 한번에 조회"""
        results = {}
        
        for coin in coins:
            print(f"📊 {coin} 가격 조회 중...")
            price_data = self.get_price_with_fallback(coin)
            
            if price_data:
                results[coin] = price_data
                print(f"  ✅ {price_data['source']}: ${price_data['price']:,.2f}")
            else:
                print(f"  ❌ 모든 API에서 실패")
            
            # API 제한 방지
            time.sleep(1)
        
        return results

def test_alternative_apis():
    """대안 API들 테스트"""
    print("🧪 대안 API 테스트 시작...")
    
    # 1. CoinPaprika 테스트
    print("\n1. CoinPaprika API 테스트")
    paprika = CoinPaprikaAPI()
    
    btc_price = paprika.get_coin_price("btc-bitcoin")
    if btc_price:
        print(f"✅ BTC 가격: ${btc_price['quotes']['USD']['price']:,.2f}")
        print(f"   24h 변동: {btc_price['quotes']['USD']['percent_change_24h']:.2f}%")
    
    # 2. CryptoCompare 테스트  
    print("\n2. CryptoCompare API 테스트")
    cc = CryptoCompareAPI()
    
    btc_cc = cc.get_price("BTC", "USD")
    if btc_cc:
        print(f"✅ BTC 가격: ${btc_cc['USD']:,.2f}")
    
    # 3. 다중 API 매니저 테스트
    print("\n3. 다중 API 매니저 테스트")
    manager = MultiAPIManager()
    
    results = manager.get_multiple_prices(['bitcoin', 'ethereum'])
    
    print("\n📊 종합 결과:")
    for coin, data in results.items():
        print(f"{coin}: ${data['price']:,.2f} (출처: {data['source']})")

def create_backup_data_collector():
    """백업 데이터 수집기 생성"""
    print("🔄 백업 데이터 수집기 설정 중...")
    
    manager = MultiAPIManager()
    
    # 주요 코인들의 현재 가격 수집
    coins = ['bitcoin', 'ethereum', 'ripple']
    all_data = manager.get_multiple_prices(coins)
    
    # 결과를 DataFrame으로 변환
    if all_data:
        df_data = []
        for coin, data in all_data.items():
            df_data.append({
                'timestamp': datetime.now(),
                'coin': coin,
                'price': data['price'],
                'source': data['source'],
                'change_24h': data.get('change_24h'),
                'market_cap': data.get('market_cap')
            })
        
        df = pd.DataFrame(df_data)
        
        # CSV로 저장
        filename = f"backup_crypto_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df.to_csv(filename, index=False)
        print(f"✅ 백업 데이터 저장: {filename}")
        
        return df
    
    return None

if __name__ == "__main__":
    # API 테스트 실행
    test_alternative_apis()
    
    print("\n" + "="*50)
    
    # 백업 데이터 수집
    backup_df = create_backup_data_collector()
    
    if backup_df is not None:
        print("\n📋 수집된 데이터:")
        print(backup_df.to_string())