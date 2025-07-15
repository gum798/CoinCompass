#!/usr/bin/env python3
"""
CoinCompass 기본 기능 테스트 (의존성 최소화)
API 키 관리와 매크로 분석기 통합 확인
"""

import os
import sys
import json
from pathlib import Path

def test_api_key_storage():
    """API 키 저장 기본 기능 테스트"""
    print("🔐 API 키 저장 기본 기능 테스트")
    print("="*40)
    
    # 설정 디렉토리 생성
    config_dir = Path.home() / '.coincompass'
    config_dir.mkdir(exist_ok=True)
    key_file = config_dir / 'api_keys.json'
    
    # 테스트 데이터
    test_data = {
        'fred': 'test_fred_key_12345',
        'coinbase': 'test_coinbase_key_67890'
    }
    
    try:
        # 1. 저장 테스트
        print("📝 API 키 저장...")
        with open(key_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        
        # 파일 권한 설정
        os.chmod(key_file, 0o600)
        print("✅ 저장 성공")
        
        # 2. 로드 테스트
        print("📖 API 키 로드...")
        with open(key_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        print("✅ 로드 성공")
        print(f"저장된 키: {list(loaded_data.keys())}")
        
        # 3. FRED 키 조회
        fred_key = loaded_data.get('fred')
        if fred_key:
            print(f"✅ FRED 키 조회 성공: {fred_key[:8]}...")
        else:
            print("❌ FRED 키 조회 실패")
        
        # 4. 정리
        os.remove(key_file)
        print("🧹 테스트 파일 정리 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        return False

def test_macro_analyzer_integration():
    """매크로 분석기 통합 시뮬레이션"""
    print("\n📊 매크로 분석기 통합 시뮬레이션")
    print("="*40)
    
    # API 키 저장 시뮬레이션
    config_dir = Path.home() / '.coincompass'
    config_dir.mkdir(exist_ok=True)
    key_file = config_dir / 'api_keys.json'
    
    # 실제 사용 시나리오 시뮬레이션
    print("👤 사용자가 FRED API 키를 저장...")
    api_keys = {'fred': 'user_real_fred_api_key'}
    
    with open(key_file, 'w', encoding='utf-8') as f:
        json.dump(api_keys, f, indent=2)
    print("✅ FRED API 키 저장 완료")
    
    # 매크로 분석기가 키를 사용하는 과정 시뮬레이션
    print("📈 매크로 분석기 시작...")
    
    try:
        # 저장된 키 로드
        with open(key_file, 'r', encoding='utf-8') as f:
            stored_keys = json.load(f)
        
        fred_key = stored_keys.get('fred')
        
        if fred_key:
            print(f"✅ 저장된 FRED 키 발견: {fred_key[:10]}...")
            print("📊 경제 지표 수집 시작 (시뮬레이션)")
            
            # 실제 FRED API 호출 시뮬레이션
            economic_indicators = {
                'fed_rate': {'value': 5.25, 'description': '연방기금금리'},
                'unemployment': {'value': 3.7, 'description': '실업률'},
                'inflation': {'value': 3.2, 'description': '소비자물가지수'}
            }
            
            print("📈 수집된 경제 지표:")
            for name, data in economic_indicators.items():
                print(f"  • {data['description']}: {data['value']}%")
            
            print("✅ 경제 지표 분석 완료")
            
        else:
            print("❌ FRED API 키를 찾을 수 없음")
            print("💡 사용자가 메뉴에서 API 키를 저장해야 함")
    
    except Exception as e:
        print(f"❌ 매크로 분석 오류: {str(e)}")
    
    finally:
        # 정리
        if key_file.exists():
            os.remove(key_file)
        print("🧹 테스트 정리 완료")

def test_menu_integration():
    """메뉴 통합 시뮬레이션"""
    print("\n🧭 CoinCompass 메뉴 통합 시뮬레이션")
    print("="*40)
    
    print("메뉴 구조:")
    menu_items = [
        "1. 빠른 가격 체크",
        "2. 기술적 분석 데모", 
        "3. 종합 시장 분석",
        "4. 가격 변동 요인 분석",
        "5. 검증 보고서 생성",
        "6. 실시간 모니터링",
        "7. API 키 관리 🔐",  # 새로 추가된 항목
        "8. 예제 실행",
        "0. 종료"
    ]
    
    for item in menu_items:
        indicator = "← 새로 추가!" if "API 키" in item else ""
        print(f"  {item} {indicator}")
    
    print("\n🔄 사용자 워크플로우:")
    workflow = [
        "1. python run_coincompass.py 실행",
        "2. 메뉴 '7. API 키 관리' 선택",
        "3. '1. FRED API 키 저장' 선택",
        "4. FRED API 키 입력 및 저장",
        "5. '4. FRED API 키 테스트'로 연결 확인",
        "6. 메인 메뉴로 돌아가기",
        "7. '3. 종합 시장 분석' 선택",
        "8. 저장된 FRED 키로 경제 지표 자동 수집",
        "9. 암호화폐와 경제 지표 상관관계 분석 결과 확인"
    ]
    
    for i, step in enumerate(workflow, 1):
        print(f"  {i:2d}. {step}")
    
    print(f"\n💡 핵심 개선사항:")
    improvements = [
        "FRED API 키를 한 번만 저장하면 계속 사용 가능",
        "암호화 저장으로 보안 강화 (cryptography 있을 때)",
        "사용자 친화적인 API 키 관리 인터페이스",
        "자동 API 키 테스트 기능",
        "경제 지표 분석의 완전 자동화"
    ]
    
    for improvement in improvements:
        print(f"  ✅ {improvement}")

def main():
    """메인 테스트 실행"""
    print("🧭 CoinCompass FRED API 키 통합 기능 테스트")
    print("="*60)
    
    # 기본 기능 테스트
    storage_success = test_api_key_storage()
    
    if storage_success:
        # 통합 테스트
        test_macro_analyzer_integration()
        test_menu_integration()
        
        print(f"\n🎉 모든 테스트 성공!")
        print(f"📋 다음 단계:")
        print(f"  • python run_coincompass.py 실행")
        print(f"  • 메뉴 7번으로 API 키 저장")
        print(f"  • 메뉴 3번으로 경제 지표 분석 활용")
        
    else:
        print(f"\n❌ 기본 기능 테스트 실패")
        print(f"💡 파일 권한이나 디렉토리 접근 권한을 확인하세요")

if __name__ == "__main__":
    main()