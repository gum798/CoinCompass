"""
다중 API 제공자 관리자
기존 multi_api_manager.py를 개선하여 재구조화
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import random

from ..core.models import PriceData, CoinData
from ..utils.logger import get_logger
from .providers.coinpaprika import CoinPaprikaProvider
from .providers.coingecko import CoinGeckoProvider

logger = get_logger(__name__)

class MultiAPIProvider:
    """다중 API 제공자 관리자"""
    
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
        logger.info(f"MultiAPIProvider 초기화: {len(self.providers)}개 제공자")
        
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
    
    def get_price_data(self, coin_id: str) -> Optional[PriceData]:
        """가격 데이터 조회 (fallback 지원)"""
        self.request_stats['total_requests'] += 1
        
        # 모든 제공자 시도
        for _ in range(len(self.providers)):
            provider = self.get_next_available_provider()
            
            if provider is None:
                logger.warning("모든 API 제공자가 일시적으로 사용 불가능")
                time.sleep(5)
                continue
            
            logger.debug(f"{provider.name} API 사용하여 {coin_id} 조회")
            result = provider.get_price(coin_id)
            
            if result:
                self.request_stats['successful_requests'] += 1
                self.request_stats['provider_usage'][provider.name] = \
                    self.request_stats['provider_usage'].get(provider.name, 0) + 1
                
                # PriceData 모델로 변환
                price_data = PriceData(
                    price=result['price'],
                    market_cap=result.get('market_cap'),
                    volume_24h=result.get('volume_24h'),
                    price_change_24h=result.get('price_change_24h'),
                    source=provider.name
                )
                
                # 다음 요청을 위해 제공자 순환
                self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
                
                return price_data
            
            # 실패시 다음 제공자로
            self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
        
        self.request_stats['failed_requests'] += 1
        logger.error(f"{coin_id} 가격 데이터 조회 실패 (모든 제공자 시도)")
        return None
    
    def get_multiple_prices(self, coin_ids: List[str], delay: float = 1.5) -> Dict[str, PriceData]:
        """여러 코인의 가격을 순차적으로 조회"""
        results = {}
        
        for coin_id in coin_ids:
            logger.info(f"💰 {coin_id} 가격 조회 중...")
            price_data = self.get_price_data(coin_id)
            
            if price_data:
                results[coin_id] = price_data
                logger.info(f"  ✅ ${price_data.price:,.2f} (출처: {price_data.source})")
            else:
                logger.warning(f"  ❌ {coin_id} 가격 조회 실패")
            
            # API 제한 방지를 위한 대기
            if len(coin_ids) > 1:
                time.sleep(delay)
        
        return results
    
    def get_top_coins(self, limit: int = 10) -> Optional[List[CoinData]]:
        """상위 코인 목록 조회"""
        for _ in range(len(self.providers)):
            provider = self.get_next_available_provider()
            
            if provider is None:
                continue
            
            logger.info(f"📊 {provider.name}에서 상위 {limit}개 코인 조회")
            result = provider.get_top_coins(limit)
            
            if result is not None:
                self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
                
                # CoinData 모델로 변환
                coins = []
                for _, row in result.iterrows():
                    price_data = PriceData(
                        price=row['current_price'],
                        market_cap=row.get('market_cap'),
                        volume_24h=row.get('total_volume'),
                        price_change_24h=row.get('price_change_percentage_24h'),
                        source=provider.name
                    )
                    
                    coin_data = CoinData(
                        id=row['id'],
                        symbol=row['symbol'],
                        name=row['name'],
                        current_price=price_data,
                        rank=getattr(row, 'rank', None)
                    )
                    coins.append(coin_data)
                
                return coins
            
            self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
        
        logger.error("상위 코인 목록 조회 실패 (모든 제공자 시도)")
        return None
    
    def reset_all_providers(self):
        """모든 제공자의 에러 카운트 리셋"""
        for provider in self.providers:
            provider.reset_errors()
        logger.info("🔄 모든 API 제공자 상태 리셋")
    
    def get_stats(self) -> Dict[str, Any]:
        """요청 통계 조회"""
        return self.request_stats.copy()
    
    def print_stats(self):
        """통계 출력"""
        stats = self.get_stats()
        success_rate = (stats['successful_requests'] / max(stats['total_requests'], 1)) * 100
        
        logger.info(f"📊 API 사용 통계:")
        logger.info(f"총 요청: {stats['total_requests']}")
        logger.info(f"성공: {stats['successful_requests']}")
        logger.info(f"실패: {stats['failed_requests']}")
        logger.info(f"성공률: {success_rate:.1f}%")
        
        if stats['provider_usage']:
            logger.info(f"제공자별 사용량:")
            for provider, count in stats['provider_usage'].items():
                logger.info(f"  - {provider}: {count}회")