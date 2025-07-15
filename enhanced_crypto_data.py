"""
향상된 암호화폐 데이터 수집기 - 다중 API 지원
기존 CoinGeckoAPI를 대체하는 향상된 버전
"""

import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
import json
from multi_api_manager import MultiAPIManager

class EnhancedCryptoAPI:
    """향상된 암호화폐 API - 다중 제공자 지원"""
    
    def __init__(self):
        self.multi_api = MultiAPIManager()
        
    def get_price(self, coin_id="bitcoin", vs_currency="usd"):
        """특정 코인의 현재 가격 조회 (다중 API 지원)"""
        result = self.multi_api.get_price_with_fallback(coin_id)
        
        if result:
            # CoinGecko API와 호환되는 형식으로 변환
            return {
                coin_id: {
                    'usd': result['price'],
                    'usd_market_cap': result['market_cap'],
                    'usd_24h_vol': result['volume_24h'],
                    'usd_24h_change': result['price_change_24h']
                }
            }
        
        return None
    
    def get_historical_data(self, coin_id="bitcoin", vs_currency="usd", days=30):
        """코인의 과거 가격 데이터 조회"""
        # 현재는 CoinGecko API만 과거 데이터 제공
        # 필요시 다른 API 추가 가능
        
        url = "https://api.coingecko.com/api/v3/coins/{}/market_chart".format(coin_id)
        params = {
            'vs_currency': vs_currency,
            'days': days,
            'interval': 'daily' if days > 1 else 'hourly'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 데이터를 DataFrame으로 변환
            prices = data['prices']
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('datetime', inplace=True)
            df.drop('timestamp', axis=1, inplace=True)
            
            return df
        except requests.exceptions.RequestException as e:
            print(f"과거 데이터 조회 오류: {e}")
            return None
    
    def get_top_coins(self, limit=100):
        """시가총액 상위 코인 목록 조회 (다중 API 지원)"""
        result = self.multi_api.get_top_coins_with_fallback(limit)
        
        if result is not None:
            # 기존 형식과 호환되도록 컬럼 정리
            try:
                return result[['id', 'symbol', 'name', 'current_price', 'market_cap', 
                              'total_volume', 'price_change_percentage_24h']]
            except KeyError:
                # CoinPaprika 형식인 경우 그대로 반환
                return result
        
        return None
    
    def get_multiple_coins_data(self, coins):
        """여러 코인 데이터를 한번에 조회"""
        return self.multi_api.get_multiple_prices(coins)
    
    def get_api_stats(self):
        """API 사용 통계 조회"""
        return self.multi_api.get_stats()
    
    def reset_api_providers(self):
        """API 제공자 상태 리셋"""
        self.multi_api.reset_all_providers()

def test_enhanced_api():
    """향상된 API 테스트"""
    print("🚀 향상된 암호화폐 API 테스트")
    
    api = EnhancedCryptoAPI()
    
    print("\n1. 비트코인 현재 가격:")
    btc_price = api.get_price("bitcoin")
    if btc_price:
        print(json.dumps(btc_price, indent=2))
    
    print("\n2. 상위 5개 코인:")
    top_coins = api.get_top_coins(5)
    if top_coins is not None:
        print(top_coins.to_string())
    
    print("\n3. 여러 코인 동시 조회:")
    multi_data = api.get_multiple_coins_data(['bitcoin', 'ethereum', 'ripple'])
    for coin, data in multi_data.items():
        print(f"{coin}: ${data['price']:,.2f} (출처: {data['source']})")
    
    print("\n4. 비트코인 7일간 가격 데이터:")
    btc_history = api.get_historical_data("bitcoin", days=7)
    if btc_history is not None:
        print(btc_history.head())
        print(f"총 {len(btc_history)}개 데이터 포인트")
    
    print("\n5. API 사용 통계:")
    api.multi_api.print_stats()

# 기존 CoinGeckoAPI와 호환성을 위한 별칭
CoinGeckoAPI = EnhancedCryptoAPI

if __name__ == "__main__":
    test_enhanced_api()