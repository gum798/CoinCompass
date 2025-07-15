"""
기본 API 제공자 클래스
"""

import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from abc import ABC, abstractmethod

from ...utils.logger import get_logger

logger = get_logger(__name__)

class BaseAPIProvider(ABC):
    """API 제공자 기본 클래스"""
    
    def __init__(self, name: str, base_url: str, rate_limit_per_minute: int = 60, requires_key: bool = False):
        self.name = name
        self.base_url = base_url
        self.rate_limit_per_minute = rate_limit_per_minute
        self.requires_key = requires_key
        self.request_times = []
        self.last_error_time = None
        self.error_count = 0
        self.is_available = True
        
    def can_make_request(self) -> bool:
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
            logger.warning(f"⚠️ {self.name} API 일시적 비활성화 (에러 {self.error_count}회)")
    
    def reset_errors(self):
        """에러 카운트 리셋"""
        self.error_count = 0
        self.is_available = True
        self.last_error_time = None
        logger.info(f"🔄 {self.name} API 상태 리셋")
    
    def make_request(self, endpoint: str, params: Dict = None, timeout: int = 10) -> Optional[Dict]:
        """HTTP 요청 실행"""
        if not self.can_make_request():
            return None
            
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params or {}, timeout=timeout)
            response.raise_for_status()
            
            self.record_request()
            return response.json()
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ {self.name} API 요청 오류: {str(e)}")
            return None
    
    @abstractmethod
    def get_price(self, coin_id: str) -> Optional[Dict]:
        """가격 조회 (각 제공자별 구현 필요)"""
        pass
    
    @abstractmethod
    def get_top_coins(self, limit: int = 10) -> Optional[List[Dict]]:
        """상위 코인 목록 조회 (각 제공자별 구현 필요)"""
        pass