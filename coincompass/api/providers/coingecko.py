"""
CoinGecko API 제공자
"""

import pandas as pd
from typing import Optional, Dict

from .base import BaseAPIProvider
from ...utils.logger import get_logger

logger = get_logger(__name__)

class CoinGeckoProvider(BaseAPIProvider):
    """CoinGecko API 제공자"""
    
    def __init__(self):
        super().__init__(
            name="CoinGecko",
            base_url="https://api.coingecko.com/api/v3",
            rate_limit_per_minute=30,
            requires_key=False
        )
    
    def get_price(self, coin_id: str) -> Optional[Dict]:
        """가격 조회"""
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }
        
        data = self.make_request("/simple/price", params=params)
        
        if data and coin_id in data:
            coin_data = data[coin_id]
            return {
                'price': coin_data['usd'],
                'market_cap': coin_data.get('usd_market_cap', 0),
                'volume_24h': coin_data.get('usd_24h_vol', 0),
                'price_change_24h': coin_data.get('usd_24h_change', 0)
            }
        
        return None
    
    def get_top_coins(self, limit: int = 10) -> Optional[pd.DataFrame]:
        """상위 코인 목록"""
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': limit,
            'page': 1,
            'sparkline': 'false'
        }
        
        data = self.make_request("/coins/markets", params=params)
        
        if data:
            df = pd.DataFrame(data)
            return df[['id', 'symbol', 'name', 'current_price', 'market_cap', 
                      'total_volume', 'price_change_percentage_24h']]
        
        return None