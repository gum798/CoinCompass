"""
CoinPaprika API 제공자
"""

import pandas as pd
from typing import Optional, Dict

from .base import BaseAPIProvider
from ...utils.logger import get_logger

logger = get_logger(__name__)

class CoinPaprikaProvider(BaseAPIProvider):
    """CoinPaprika API 제공자"""
    
    def __init__(self):
        super().__init__(
            name="CoinPaprika",
            base_url="https://api.coinpaprika.com/v1",
            rate_limit_per_minute=50,
            requires_key=False
        )
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
    
    def get_price(self, coin_id: str) -> Optional[Dict]:
        """가격 조회"""
        paprika_id = self.coin_id_map.get(coin_id, coin_id)
        data = self.make_request(f"/tickers/{paprika_id}")
        
        if data and 'quotes' in data and 'USD' in data['quotes']:
            usd_data = data['quotes']['USD']
            return {
                'price': usd_data['price'],
                'market_cap': usd_data['market_cap'],
                'volume_24h': usd_data['volume_24h'],
                'price_change_24h': usd_data['percent_change_24h']
            }
        
        return None
    
    def get_top_coins(self, limit: int = 10) -> Optional[pd.DataFrame]:
        """상위 코인 목록"""
        data = self.make_request("/tickers", params={'limit': limit})
        
        if data:
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
        
        return None