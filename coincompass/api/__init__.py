"""
CoinCompass API Module

다양한 암호화폐 데이터 API 제공자를 통합 관리
"""

from .multi_provider import MultiAPIProvider
from .providers.coinpaprika import CoinPaprikaProvider
from .providers.coingecko import CoinGeckoProvider

__all__ = ["MultiAPIProvider", "CoinPaprikaProvider", "CoinGeckoProvider"]