import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
import json
from multi_api_manager import MultiAPIManager

class CoinGeckoAPI:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        
    def get_price(self, coin_id="bitcoin", vs_currency="usd"):
        """특정 코인의 현재 가격 조회"""
        url = f"{self.base_url}/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': vs_currency,
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return None
    
    def get_historical_data(self, coin_id="bitcoin", vs_currency="usd", days=30):
        """코인의 과거 가격 데이터 조회"""
        url = f"{self.base_url}/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': vs_currency,
            'days': days,
            'interval': 'daily' if days > 1 else 'hourly'
        }
        
        try:
            response = requests.get(url, params=params)
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
            print(f"API 요청 오류: {e}")
            return None
    
    def get_top_coins(self, limit=100):
        """시가총액 상위 코인 목록 조회"""
        url = f"{self.base_url}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': limit,
            'page': 1,
            'sparkline': 'false'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            df = pd.DataFrame(data)
            return df[['id', 'symbol', 'name', 'current_price', 'market_cap', 
                      'total_volume', 'price_change_percentage_24h']]
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return None

def test_api():
    """API 연동 테스트"""
    api = CoinGeckoAPI()
    
    print("=== CoinGecko API 테스트 ===")
    
    # 1. 비트코인 현재 가격
    print("\n1. 비트코인 현재 가격:")
    btc_price = api.get_price("bitcoin")
    if btc_price:
        print(json.dumps(btc_price, indent=2))
    
    # 2. 상위 10개 코인
    print("\n2. 시가총액 상위 10개 코인:")
    top_coins = api.get_top_coins(10)
    if top_coins is not None:
        print(top_coins.to_string())
    
    # 3. 비트코인 7일간 가격 데이터
    print("\n3. 비트코인 7일간 가격 데이터:")
    btc_history = api.get_historical_data("bitcoin", days=7)
    if btc_history is not None:
        print(btc_history.head())
        print(f"총 {len(btc_history)}개 데이터 포인트")

if __name__ == "__main__":
    test_api()