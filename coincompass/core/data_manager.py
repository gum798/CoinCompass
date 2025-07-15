"""
데이터 관리자 - 모든 데이터 소스를 통합 관리
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import json
import os

from ..utils.logger import get_logger
from ..config.settings import Settings

logger = get_logger(__name__)

class DataManager:
    """중앙 데이터 관리자"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.settings = Settings(config_path)
        self.cache = {}
        self.cache_timeout = timedelta(minutes=5)
        
    def get_cached_data(self, key: str) -> Optional[Dict]:
        """캐시된 데이터 조회"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.cache_timeout:
                return data
            else:
                del self.cache[key]
        return None
    
    def set_cached_data(self, key: str, data: Dict) -> None:
        """데이터 캐시 저장"""
        self.cache[key] = (data, datetime.now())
    
    def save_to_file(self, data: Union[Dict, pd.DataFrame], filename: str, 
                     directory: str = "data") -> str:
        """데이터를 파일로 저장"""
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, filename)
        
        if isinstance(data, pd.DataFrame):
            data.to_csv(filepath, index=False)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"데이터 저장: {filepath}")
        return filepath
    
    def load_from_file(self, filepath: str) -> Union[Dict, pd.DataFrame]:
        """파일에서 데이터 로드"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}")
        
        if filepath.endswith('.csv'):
            return pd.read_csv(filepath)
        elif filepath.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {filepath}")
    
    def cleanup_old_data(self, directory: str, days: int = 7) -> None:
        """오래된 데이터 파일 정리"""
        if not os.path.exists(directory):
            return
            
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                if file_time < cutoff_date:
                    os.remove(filepath)
                    logger.info(f"오래된 파일 삭제: {filepath}")
    
    def get_data_stats(self) -> Dict:
        """데이터 통계 조회"""
        return {
            'cache_size': len(self.cache),
            'cache_keys': list(self.cache.keys()),
            'settings': self.settings.get_summary()
        }