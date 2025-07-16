"""
API 키 관리 모듈
암호화된 API 키 저장 및 로드 기능
"""

import os
import json
from typing import Dict, Optional
from pathlib import Path

try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

try:
    from ..utils.logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    # 상대 임포트 실패 시 간단한 로거 사용
    class SimpleLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def debug(self, msg): print(f"DEBUG: {msg}")
    logger = SimpleLogger()

class APIKeyManager:
    """API 키 관리자"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / '.coincompass'
        self.config_dir.mkdir(exist_ok=True)
        
        self.key_file = self.config_dir / 'api_keys.enc'
        self.master_key_file = self.config_dir / 'master.key'
        
        self._ensure_master_key()
    
    def _ensure_master_key(self):
        """마스터 키 생성 또는 로드"""
        if not CRYPTOGRAPHY_AVAILABLE:
            logger.warning("cryptography 라이브러리가 없어 암호화를 사용할 수 없습니다")
            self.fernet = None
            return
            
        if not self.master_key_file.exists():
            # 새로운 마스터 키 생성
            key = Fernet.generate_key()
            with open(self.master_key_file, 'wb') as f:
                f.write(key)
            # 파일 권한을 사용자만 읽기 가능하도록 설정
            os.chmod(self.master_key_file, 0o600)
            logger.info("새로운 마스터 키가 생성되었습니다")
        
        with open(self.master_key_file, 'rb') as f:
            self.master_key = f.read()
        
        self.fernet = Fernet(self.master_key)
    
    def save_api_key(self, service: str, api_key: str) -> bool:
        """API 키 저장"""
        try:
            # 기존 키들 로드
            api_keys = self.load_all_api_keys()
            
            # 새 키 추가
            api_keys[service] = api_key
            
            if self.fernet is not None:
                # 암호화하여 저장
                encrypted_data = self.fernet.encrypt(json.dumps(api_keys).encode())
                
                with open(self.key_file, 'wb') as f:
                    f.write(encrypted_data)
            else:
                # 평문으로 저장 (fallback)
                logger.warning("암호화 라이브러리가 없어 평문으로 API 키를 저장합니다")
                plaintext_file = self.config_dir / 'api_keys.json'
                with open(plaintext_file, 'w', encoding='utf-8') as f:
                    json.dump(api_keys, f, indent=2)
                self.key_file = plaintext_file  # 파일 경로 업데이트
            
            # 파일 권한 설정
            os.chmod(self.key_file, 0o600)
            
            logger.info(f"{service} API 키가 저장되었습니다")
            return True
            
        except Exception as e:
            logger.error(f"API 키 저장 실패: {str(e)}")
            return False
    
    def load_api_key(self, service: str) -> Optional[str]:
        """특정 서비스의 API 키 로드"""
        try:
            api_keys = self.load_all_api_keys()
            return api_keys.get(service)
        except Exception as e:
            logger.error(f"API 키 로드 실패: {str(e)}")
            return None
    
    def load_all_api_keys(self) -> Dict[str, str]:
        """모든 API 키 로드"""
        try:
            # 암호화된 파일 먼저 확인
            if self.fernet is not None and self.key_file.exists():
                with open(self.key_file, 'rb') as f:
                    encrypted_data = f.read()
                
                decrypted_data = self.fernet.decrypt(encrypted_data)
                return json.loads(decrypted_data.decode())
            
            # 평문 파일 확인 (fallback)
            plaintext_file = self.config_dir / 'api_keys.json'
            if plaintext_file.exists():
                with open(plaintext_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return {}
            
        except Exception as e:
            logger.error(f"API 키 로드 실패: {str(e)}")
            return {}
    
    def delete_api_key(self, service: str) -> bool:
        """API 키 삭제"""
        try:
            api_keys = self.load_all_api_keys()
            
            if service in api_keys:
                del api_keys[service]
                
                if self.fernet is not None:
                    # 암호화하여 저장
                    encrypted_data = self.fernet.encrypt(json.dumps(api_keys).encode())
                    
                    with open(self.key_file, 'wb') as f:
                        f.write(encrypted_data)
                else:
                    # 평문으로 저장 (fallback)
                    plaintext_file = self.config_dir / 'api_keys.json'
                    with open(plaintext_file, 'w', encoding='utf-8') as f:
                        json.dump(api_keys, f, indent=2)
                
                logger.info(f"{service} API 키가 삭제되었습니다")
                return True
            else:
                logger.warning(f"{service} API 키를 찾을 수 없습니다")
                return False
                
        except Exception as e:
            logger.error(f"API 키 삭제 실패: {str(e)}")
            return False
    
    def list_services(self) -> list:
        """저장된 서비스 목록 반환"""
        try:
            api_keys = self.load_all_api_keys()
            return list(api_keys.keys())
        except Exception as e:
            logger.error(f"서비스 목록 조회 실패: {str(e)}")
            return []
    
    def has_api_key(self, service: str) -> bool:
        """특정 서비스의 API 키 존재 여부 확인"""
        return service in self.load_all_api_keys()

class SimplePlaintextAPIKeyManager:
    """간단한 평문 API 키 관리자 (cryptography 라이브러리가 없는 경우)"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / '.coincompass'
        self.config_dir.mkdir(exist_ok=True)
        
        self.key_file = self.config_dir / 'api_keys.json'
    
    def save_api_key(self, service: str, api_key: str) -> bool:
        """API 키 저장 (평문)"""
        try:
            api_keys = self.load_all_api_keys()
            api_keys[service] = api_key
            
            with open(self.key_file, 'w', encoding='utf-8') as f:
                json.dump(api_keys, f, indent=2)
            
            # 파일 권한 설정
            os.chmod(self.key_file, 0o600)
            
            logger.info(f"{service} API 키가 저장되었습니다")
            return True
            
        except Exception as e:
            logger.error(f"API 키 저장 실패: {str(e)}")
            return False
    
    def load_api_key(self, service: str) -> Optional[str]:
        """특정 서비스의 API 키 로드"""
        try:
            api_keys = self.load_all_api_keys()
            return api_keys.get(service)
        except Exception as e:
            logger.error(f"API 키 로드 실패: {str(e)}")
            return None
    
    def load_all_api_keys(self) -> Dict[str, str]:
        """모든 API 키 로드"""
        try:
            if not self.key_file.exists():
                return {}
            
            with open(self.key_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"API 키 로드 실패: {str(e)}")
            return {}
    
    def delete_api_key(self, service: str) -> bool:
        """API 키 삭제"""
        try:
            api_keys = self.load_all_api_keys()
            
            if service in api_keys:
                del api_keys[service]
                
                with open(self.key_file, 'w', encoding='utf-8') as f:
                    json.dump(api_keys, f, indent=2)
                
                logger.info(f"{service} API 키가 삭제되었습니다")
                return True
            else:
                logger.warning(f"{service} API 키를 찾을 수 없습니다")
                return False
                
        except Exception as e:
            logger.error(f"API 키 삭제 실패: {str(e)}")
            return False
    
    def list_services(self) -> list:
        """저장된 서비스 목록 반환"""
        try:
            api_keys = self.load_all_api_keys()
            return list(api_keys.keys())
        except Exception as e:
            logger.error(f"서비스 목록 조회 실패: {str(e)}")
            return []
    
    def has_api_key(self, service: str) -> bool:
        """특정 서비스의 API 키 존재 여부 확인"""
        return service in self.load_all_api_keys()

def get_api_key_manager():
    """API 키 관리자 인스턴스 반환"""
    if CRYPTOGRAPHY_AVAILABLE:
        return APIKeyManager()
    else:
        logger.warning("암호화 라이브러리가 없어 평문으로 API 키를 저장합니다")
        return SimplePlaintextAPIKeyManager()

def demo_api_key_management():
    """API 키 관리 데모"""
    print("🔐 API 키 관리 시스템 데모")
    print("=" * 50)
    
    manager = get_api_key_manager()
    
    # 테스트 키 저장
    print("📝 FRED API 키 저장 테스트...")
    test_key = "test_fred_api_key_12345"
    success = manager.save_api_key("fred", test_key)
    print(f"저장 결과: {'✅ 성공' if success else '❌ 실패'}")
    
    # 키 로드 테스트
    print("\n📖 API 키 로드 테스트...")
    loaded_key = manager.load_api_key("fred")
    if loaded_key:
        print(f"로드된 키: {loaded_key[:10]}...{loaded_key[-5:]}")  # 일부만 표시
        print("✅ API 키 로드 성공")
    else:
        print("❌ API 키 로드 실패")
    
    # 서비스 목록 조회
    print("\n📋 저장된 서비스 목록:")
    services = manager.list_services()
    for service in services:
        print(f"  • {service}")
    
    # 테스트 키 삭제
    print("\n🗑️ 테스트 키 삭제...")
    delete_success = manager.delete_api_key("fred")
    print(f"삭제 결과: {'✅ 성공' if delete_success else '❌ 실패'}")

if __name__ == "__main__":
    demo_api_key_management()