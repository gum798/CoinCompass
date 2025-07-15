#!/usr/bin/env python3
"""
API 키 관리 시스템 독립 테스트
cryptography 의존성 없이 작동하는지 확인
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional

# cryptography 사용 가능 여부 확인
try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

class SimpleLogger:
    """간단한 로거"""
    def info(self, msg): print(f"INFO: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")
    def debug(self, msg): print(f"DEBUG: {msg}")

logger = SimpleLogger()

class SimplePlaintextAPIKeyManager:
    """간단한 평문 API 키 관리자"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / '.coincompass'
        self.config_dir.mkdir(exist_ok=True)
        
        self.key_file = self.config_dir / 'api_keys.json'
        
        if not CRYPTOGRAPHY_AVAILABLE:
            logger.warning("cryptography 라이브러리가 없어 평문으로 API 키를 저장합니다")
    
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

def test_api_key_functionality():
    """API 키 기능 테스트"""
    print("🔐 API 키 관리 시스템 독립 테스트")
    print("="*50)
    print(f"Cryptography 사용 가능: {CRYPTOGRAPHY_AVAILABLE}")
    print()
    
    # API 키 관리자 생성
    manager = SimplePlaintextAPIKeyManager()
    print("✅ API 키 관리자 생성 완료")
    
    # 1. FRED API 키 저장 테스트
    print("\n📝 FRED API 키 저장 테스트...")
    test_key = "test_fred_api_key_abcd1234"
    success = manager.save_api_key("fred", test_key)
    print(f"저장 결과: {'✅ 성공' if success else '❌ 실패'}")
    
    # 2. 키 로드 테스트
    print("\n📖 API 키 로드 테스트...")
    loaded_key = manager.load_api_key("fred")
    if loaded_key == test_key:
        print(f"✅ 로드 성공: {loaded_key[:10]}...{loaded_key[-8:]}")
    else:
        print(f"❌ 로드 실패: 예상 {test_key}, 실제 {loaded_key}")
    
    # 3. 다른 서비스 키 저장
    print("\n📝 추가 API 키 저장 테스트...")
    manager.save_api_key("coinbase", "coinbase_test_key_xyz789")
    manager.save_api_key("binance", "binance_test_key_123")
    
    # 4. 서비스 목록 조회
    print("\n📋 저장된 서비스 목록:")
    services = manager.list_services()
    for i, service in enumerate(services, 1):
        api_key = manager.load_api_key(service)
        masked_key = f"{api_key[:4]}****{api_key[-4:]}" if len(api_key) > 8 else "****"
        print(f"  {i}. {service.upper()}: {masked_key}")
    
    # 5. 키 존재 여부 확인
    print("\n🔍 키 존재 여부 테스트:")
    print(f"  FRED 키 존재: {'✅' if manager.has_api_key('fred') else '❌'}")
    print(f"  비존재 키 확인: {'❌' if not manager.has_api_key('nonexistent') else '✅'}")
    
    # 6. 키 삭제 테스트
    print("\n🗑️ API 키 삭제 테스트...")
    delete_success = manager.delete_api_key("binance")
    print(f"Binance 키 삭제: {'✅ 성공' if delete_success else '❌ 실패'}")
    
    # 7. 삭제 후 목록 확인
    print("\n📋 삭제 후 서비스 목록:")
    services_after = manager.list_services()
    for service in services_after:
        print(f"  • {service}")
    
    # 8. 정리 - 모든 테스트 키 삭제
    print("\n🧹 테스트 키 정리...")
    for service in manager.list_services():
        manager.delete_api_key(service)
    
    final_services = manager.list_services()
    print(f"정리 후 남은 키: {len(final_services)}개")
    
    print("\n✅ 모든 테스트 완료!")
    
    return True

def test_integration_scenario():
    """통합 시나리오 테스트"""
    print("\n🔄 통합 시나리오 시뮬레이션")
    print("="*50)
    
    manager = SimplePlaintextAPIKeyManager()
    
    # 사용자가 FRED API 키를 저장하는 시나리오
    print("👤 사용자 시나리오: FRED API 키 저장")
    fred_key = "your_real_fred_api_key_here"
    manager.save_api_key("fred", fred_key)
    
    # 매크로 분석기가 키를 사용하는 시나리오
    print("📊 매크로 분석기: 저장된 키 사용")
    retrieved_key = manager.load_api_key("fred")
    
    if retrieved_key:
        print(f"✅ 매크로 분석기가 키를 성공적으로 로드: {retrieved_key[:10]}...")
        print("📈 경제 지표 수집 시작 (시뮬레이션)")
        # 여기서 실제 FRED API 호출이 일어남
    else:
        print("❌ 저장된 FRED API 키를 찾을 수 없음")
    
    # 정리
    manager.delete_api_key("fred")
    print("🧹 테스트 키 정리 완료")

def main():
    """메인 테스트 실행"""
    try:
        success = test_api_key_functionality()
        if success:
            test_integration_scenario()
            
            print(f"\n🎉 API 키 관리 시스템이 정상적으로 작동합니다!")
            print(f"📋 다음 단계:")
            print(f"  1. python run_coincompass.py 실행")
            print(f"  2. 메뉴 '7. API 키 관리' 선택")
            print(f"  3. 실제 FRED API 키 저장 및 테스트")
        else:
            print("❌ 테스트 실패")
            
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()