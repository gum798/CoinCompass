"""
설정 관리자
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class MonitoringConfig:
    """모니터링 설정"""
    interval_seconds: int = 1800  # 30분
    coins: list = None
    rsi_oversold: float = 30.0
    rsi_overbought: float = 70.0
    price_change_threshold: float = 5.0
    enable_alerts: bool = True
    
    def __post_init__(self):
        if self.coins is None:
            self.coins = ["bitcoin", "ethereum", "ripple", "solana", "dogecoin"]

@dataclass
class APIConfig:
    """API 설정"""
    coingecko_api_key: Optional[str] = None
    coinmarketcap_api_key: Optional[str] = None
    request_timeout: int = 10
    max_retries: int = 3
    rate_limit_buffer: float = 0.1  # 10% 버퍼

@dataclass
class DataConfig:
    """데이터 설정"""
    cache_timeout_minutes: int = 5
    data_retention_days: int = 30
    auto_cleanup: bool = True
    backup_enabled: bool = True

@dataclass
class LoggingConfig:
    """로깅 설정"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    file_path: str = "coincompass.log"
    max_file_size_mb: int = 10
    backup_count: int = 5

class Settings:
    """통합 설정 관리자"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/settings.json"
        self.monitoring = MonitoringConfig()
        self.api = APIConfig()
        self.data = DataConfig()
        self.logging = LoggingConfig()
        
        self.load_config()
        self.load_env_variables()
    
    def load_config(self):
        """설정 파일에서 로드"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 각 섹션별 설정 업데이트
                if 'monitoring' in config_data:
                    self._update_dataclass(self.monitoring, config_data['monitoring'])
                
                if 'api' in config_data:
                    self._update_dataclass(self.api, config_data['api'])
                
                if 'data' in config_data:
                    self._update_dataclass(self.data, config_data['data'])
                
                if 'logging' in config_data:
                    self._update_dataclass(self.logging, config_data['logging'])
                    
            except Exception as e:
                print(f"설정 파일 로드 오류: {e}")
        else:
            # 기본 설정 파일 생성
            self.save_config()
    
    def load_env_variables(self):
        """환경 변수에서 로드"""
        # API 키들
        if os.getenv('COINGECKO_API_KEY'):
            self.api.coingecko_api_key = os.getenv('COINGECKO_API_KEY')
        
        if os.getenv('COINMARKETCAP_API_KEY'):
            self.api.coinmarketcap_api_key = os.getenv('COINMARKETCAP_API_KEY')
        
        # 로그 레벨
        if os.getenv('LOG_LEVEL'):
            self.logging.level = os.getenv('LOG_LEVEL')
    
    def save_config(self):
        """설정을 파일에 저장"""
        config_data = {
            'monitoring': asdict(self.monitoring),
            'api': asdict(self.api),
            'data': asdict(self.data),
            'logging': asdict(self.logging)
        }
        
        # 디렉토리 생성
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def _update_dataclass(self, dataclass_instance, data_dict):
        """데이터클래스 인스턴스를 딕셔너리로 업데이트"""
        for key, value in data_dict.items():
            if hasattr(dataclass_instance, key):
                setattr(dataclass_instance, key, value)
    
    def get_summary(self) -> Dict[str, Any]:
        """설정 요약 조회"""
        return {
            'config_path': self.config_path,
            'monitoring_coins': len(self.monitoring.coins),
            'monitoring_interval': self.monitoring.interval_seconds,
            'api_keys_configured': {
                'coingecko': bool(self.api.coingecko_api_key),
                'coinmarketcap': bool(self.api.coinmarketcap_api_key)
            },
            'logging_level': self.logging.level,
            'data_retention_days': self.data.data_retention_days
        }
    
    def update_monitoring_coins(self, coins: list):
        """모니터링 코인 업데이트"""
        self.monitoring.coins = coins
        self.save_config()
    
    def update_monitoring_interval(self, seconds: int):
        """모니터링 간격 업데이트"""
        self.monitoring.interval_seconds = seconds
        self.save_config()
    
    def get_coins_list(self) -> list:
        """모니터링 대상 코인 목록"""
        return self.monitoring.coins.copy()
    
    def get_api_timeout(self) -> int:
        """API 타임아웃 설정"""
        return self.api.request_timeout