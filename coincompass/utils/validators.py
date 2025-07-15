"""
데이터 검증 유틸리티
"""

import re
from typing import List, Optional

def validate_coin_id(coin_id: str) -> bool:
    """코인 ID 유효성 검증"""
    if not coin_id or not isinstance(coin_id, str):
        return False
    
    # 기본적인 패턴 검증 (소문자, 숫자, 하이픈)
    pattern = r'^[a-z0-9-]+$'
    return bool(re.match(pattern, coin_id)) and len(coin_id) <= 50

def validate_timeframe(timeframe: str) -> bool:
    """시간 프레임 유효성 검증"""
    valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']
    return timeframe in valid_timeframes

def validate_percentage(value: float) -> bool:
    """퍼센트 값 유효성 검증"""
    return isinstance(value, (int, float)) and -100 <= value <= 10000

def validate_price(price: float) -> bool:
    """가격 유효성 검증"""
    return isinstance(price, (int, float)) and price > 0

def validate_coin_list(coins: List[str]) -> List[str]:
    """코인 목록 검증 및 필터링"""
    if not isinstance(coins, list):
        return []
    
    return [coin for coin in coins if validate_coin_id(coin)]

def validate_config_value(key: str, value, expected_type) -> bool:
    """설정 값 유효성 검증"""
    if not isinstance(value, expected_type):
        return False
    
    # 특별한 검증 규칙들
    if key == 'interval_seconds' and isinstance(value, int):
        return 60 <= value <= 86400  # 1분 ~ 24시간
    
    if key == 'rsi_oversold' and isinstance(value, (int, float)):
        return 0 <= value <= 50
    
    if key == 'rsi_overbought' and isinstance(value, (int, float)):
        return 50 <= value <= 100
    
    if key == 'price_change_threshold' and isinstance(value, (int, float)):
        return 0 < value <= 100
    
    return True