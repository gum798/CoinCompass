#!/usr/bin/env python3
"""
FRED API 키 검증 테스트
사용자가 발급받은 FRED API 키를 테스트하고 저장하는 스크립트
"""

import sys
import os
import requests
from datetime import datetime, timedelta

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_fred_api_key(api_key):
    """FRED API 키 검증 테스트"""
    print(f"🧪 FRED API 키 검증 테스트")
    print("="*50)
    
    if not api_key or len(api_key) < 10:
        print("❌ API 키가 너무 짧습니다. 올바른 FRED API 키를 입력하세요.")
        return False
    
    # FRED API 테스트 호출
    fred_url = 'https://api.stlouisfed.org/fred/series/observations'
    test_series = 'FEDFUNDS'  # 연방기금금리
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    params = {
        'series_id': test_series,
        'api_key': api_key,
        'file_type': 'json',
        'observation_start': start_date.strftime('%Y-%m-%d'),
        'observation_end': end_date.strftime('%Y-%m-%d'),
        'sort_order': 'desc',
        'limit': 1
    }
    
    try:
        print(f"📡 FRED API 연결 테스트 중...")
        print(f"   URL: {fred_url}")
        print(f"   시리즈: {test_series} (연방기금금리)")
        
        response = requests.get(fred_url, params=params, timeout=10)
        print(f"   응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   응답 데이터: ✅ 수신 성공")
            
            if 'observations' in data and data['observations']:
                latest = data['observations'][0]
                if latest['value'] != '.':  # FRED에서 결측값은 '.'으로 표시
                    print(f"✅ FRED API 키 검증 성공!")
                    print(f"   📊 연방기금금리: {latest['value']}% ({latest['date']})")
                    return True, latest
                else:
                    print(f"⚠️ 데이터는 수신되었지만 값이 없습니다.")
                    print(f"   날짜: {latest['date']}, 값: {latest['value']}")
                    return True, latest
            else:
                print(f"⚠️ API 연결은 성공했지만 데이터가 없습니다.")
                print(f"   응답: {data}")
                return True, None
        
        elif response.status_code == 400:
            print(f"❌ API 키가 잘못되었거나 요청이 잘못되었습니다.")
            print(f"   오류: {response.text}")
            return False, None
            
        elif response.status_code == 429:
            print(f"⚠️ API 호출 한도 초과. 잠시 후 다시 시도하세요.")
            return False, None
            
        else:
            print(f"❌ API 호출 실패: HTTP {response.status_code}")
            print(f"   응답: {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        print(f"❌ API 호출 시간 초과 (10초)")
        return False, None
        
    except requests.exceptions.ConnectionError:
        print(f"❌ 인터넷 연결 오류. 네트워크 상태를 확인하세요.")
        return False, None
        
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {str(e)}")
        return False, None

def save_fred_key_to_coincompass(api_key):
    """CoinCompass에 FRED API 키 저장"""
    print(f"\n💾 CoinCompass에 FRED API 키 저장 중...")
    
    try:
        from coincompass.config.api_keys import get_api_key_manager
        
        manager = get_api_key_manager()
        success = manager.save_api_key('fred', api_key)
        
        if success:
            print(f"✅ FRED API 키가 CoinCompass에 성공적으로 저장되었습니다!")
            print(f"   설정 위치: ~/.coincompass/")
            
            # 저장된 키 확인
            stored_key = manager.load_api_key('fred')
            if stored_key == api_key:
                print(f"✅ 저장된 키 검증 완료")
                return True
            else:
                print(f"❌ 저장된 키 검증 실패")
                return False
        else:
            print(f"❌ API 키 저장에 실패했습니다.")
            return False
            
    except Exception as e:
        print(f"❌ CoinCompass 연동 오류: {str(e)}")
        return False

def test_coincompass_integration():
    """CoinCompass 통합 테스트"""
    print(f"\n🧭 CoinCompass 매크로 분석기 통합 테스트")
    print("="*50)
    
    try:
        from coincompass.analysis.macro import MacroeconomicAnalyzer
        from coincompass.config.api_keys import get_api_key_manager
        
        # API 키 관리자에서 FRED 키 로드
        api_manager = get_api_key_manager()
        stored_fred_key = api_manager.load_api_key('fred')
        
        if not stored_fred_key:
            print("❌ 저장된 FRED API 키를 찾을 수 없습니다.")
            return False
        
        print(f"✅ 저장된 FRED API 키 발견: {stored_fred_key[:8]}...")
        
        # 매크로 분석기 테스트
        analyzer = MacroeconomicAnalyzer()
        print(f"📊 경제 지표 수집 테스트 중...")
        
        # 실제 경제 지표 수집 테스트
        indicators = analyzer.get_economic_indicators()  # 저장된 키 자동 사용
        
        if indicators:
            print(f"✅ 경제 지표 수집 성공!")
            
            # FRED 데이터 확인
            fred_data_found = False
            for key, value in indicators.items():
                if key in ['fed_rate', 'unemployment', 'cpi', 'gdp']:
                    if isinstance(value, dict) and 'value' in value:
                        print(f"   📈 {key}: {value['value']} ({value.get('date', 'N/A')})")
                        fred_data_found = True
            
            if not fred_data_found:
                print(f"⚠️ FRED 데이터는 수집되지 않았지만 시장 데이터는 수집됨")
                
                # 시장 데이터 확인
                if 'market_indices' in indicators:
                    market_data = indicators['market_indices']
                    print(f"   💹 시장 데이터:")
                    for name, data in list(market_data.items())[:3]:
                        print(f"      {name}: ${data.get('price', 'N/A'):.2f}")
            
            return True
        else:
            print(f"❌ 경제 지표 수집 실패")
            return False
            
    except Exception as e:
        print(f"❌ CoinCompass 통합 테스트 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 실행 함수"""
    print("🧭 CoinCompass FRED API 키 검증 도구")
    print("="*60)
    
    # 사용자로부터 API 키 입력받기
    print("📋 FRED API 키를 입력하세요:")
    print("   발급 사이트: https://fred.stlouisfed.org/docs/api/api_key.html")
    print("   형식 예시: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6")
    print()
    
    api_key = input("FRED API 키: ").strip()
    
    if not api_key:
        print("❌ API 키가 입력되지 않았습니다.")
        return
    
    print(f"\n🔍 입력된 API 키: {api_key[:8]}...{api_key[-4:]} (길이: {len(api_key)})")
    
    # 1. FRED API 키 검증
    is_valid, test_data = test_fred_api_key(api_key)
    
    if not is_valid:
        print(f"\n❌ FRED API 키 검증 실패")
        print(f"💡 해결 방법:")
        print(f"   1. API 키가 올바른지 확인")
        print(f"   2. https://fred.stlouisfed.org 에서 키 재발급")
        print(f"   3. 네트워크 연결 상태 확인")
        return
    
    # 2. CoinCompass에 키 저장
    save_success = save_fred_key_to_coincompass(api_key)
    
    if not save_success:
        print(f"\n⚠️ API 키는 유효하지만 저장에 실패했습니다.")
        return
    
    # 3. CoinCompass 통합 테스트
    integration_success = test_coincompass_integration()
    
    # 최종 결과
    print(f"\n🎯 검증 결과 요약")
    print("="*50)
    print(f"✅ FRED API 키 유효성: {'통과' if is_valid else '실패'}")
    print(f"✅ CoinCompass 저장: {'성공' if save_success else '실패'}")
    print(f"✅ 통합 테스트: {'성공' if integration_success else '실패'}")
    
    if is_valid and save_success and integration_success:
        print(f"\n🎉 모든 검증 완료! CoinCompass에서 FRED 데이터를 사용할 수 있습니다.")
        print(f"📋 다음 단계:")
        print(f"   1. python3 run_coincompass.py 실행")
        print(f"   2. 메뉴 3번: '종합 시장 분석' 선택")
        print(f"   3. 저장된 FRED 키로 경제 지표 자동 분석")
    else:
        print(f"\n⚠️ 일부 검증에 실패했습니다. 위의 오류 메시지를 확인하세요.")

if __name__ == "__main__":
    main()