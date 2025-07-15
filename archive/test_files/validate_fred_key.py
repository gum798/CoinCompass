#!/usr/bin/env python3
"""
FRED API 키 검증 스크립트 (비대화형)
발급받은 FRED API 키를 이 스크립트에 넣어서 검증하세요
"""

import sys
import os
import requests
from datetime import datetime, timedelta

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# ⭐ 여기에 발급받은 FRED API 키를 입력하세요 ⭐
FRED_API_KEY = "43bd0b6e8ce7f493a95ee1160a9562a7"

def test_fred_api_directly(api_key):
    """FRED API 직접 테스트"""
    print(f"🧪 FRED API 키 직접 검증")
    print("="*50)
    
    if not api_key or api_key == "여기에_발급받은_FRED_API_키_입력":
        print("❌ API 키를 스크립트에 입력하세요!")
        print("   1. validate_fred_key.py 파일을 열어서")
        print("   2. FRED_API_KEY = \"여기에_발급받은_FRED_API_키_입력\" 부분을")
        print("   3. FRED_API_KEY = \"실제_발급받은_키\" 로 수정하세요")
        return False
    
    print(f"🔍 API 키: {api_key[:8]}...{api_key[-4:]} (길이: {len(api_key)})")
    
    # FRED API 테스트 호출
    fred_url = 'https://api.stlouisfed.org/fred/series/observations'
    
    # 여러 시리즈로 테스트
    test_series = [
        ('FEDFUNDS', '연방기금금리'),
        ('UNRATE', '실업률'),
        ('CPIAUCSL', '소비자물가지수')
    ]
    
    success_count = 0
    
    for series_id, description in test_series:
        print(f"\n📊 {description} ({series_id}) 테스트 중...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)
        
        params = {
            'series_id': series_id,
            'api_key': api_key,
            'file_type': 'json',
            'observation_start': start_date.strftime('%Y-%m-%d'),
            'observation_end': end_date.strftime('%Y-%m-%d'),
            'sort_order': 'desc',
            'limit': 3
        }
        
        try:
            response = requests.get(fred_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'observations' in data and data['observations']:
                    # 유효한 데이터 찾기
                    valid_obs = [obs for obs in data['observations'] if obs['value'] != '.']
                    
                    if valid_obs:
                        latest = valid_obs[0]
                        print(f"   ✅ 성공: {latest['value']} ({latest['date']})")
                        success_count += 1
                    else:
                        print(f"   ⚠️ 데이터 수신 성공하지만 최근 값 없음")
                        success_count += 1
                else:
                    print(f"   ⚠️ 응답 성공하지만 데이터 없음")
                    
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error_message', 'Bad Request')
                print(f"   ❌ 요청 오류: {error_msg}")
                
                if 'api_key' in error_msg.lower():
                    print(f"      💡 API 키가 잘못되었을 가능성이 높습니다.")
                    
            elif response.status_code == 429:
                print(f"   ⚠️ API 호출 한도 초과")
                
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text[:100]}")
                
        except requests.exceptions.Timeout:
            print(f"   ❌ 타임아웃 (10초)")
            
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 연결 오류")
            
        except Exception as e:
            print(f"   ❌ 오류: {str(e)}")
    
    print(f"\n📊 테스트 결과: {success_count}/{len(test_series)} 성공")
    
    if success_count >= 1:
        print(f"✅ FRED API 키가 유효합니다!")
        return True
    else:
        print(f"❌ FRED API 키에 문제가 있습니다.")
        return False

def save_to_coincompass(api_key):
    """CoinCompass에 저장"""
    print(f"\n💾 CoinCompass에 저장 중...")
    
    try:
        from coincompass.config.api_keys import get_api_key_manager
        
        manager = get_api_key_manager()
        success = manager.save_api_key('fred', api_key)
        
        if success:
            print(f"✅ CoinCompass에 저장 성공!")
            
            # 저장 확인
            stored = manager.load_api_key('fred')
            if stored == api_key:
                print(f"✅ 저장된 키 검증 완료")
                return True
            else:
                print(f"❌ 저장된 키 불일치")
                return False
        else:
            print(f"❌ 저장 실패")
            return False
            
    except Exception as e:
        print(f"❌ CoinCompass 저장 오류: {str(e)}")
        return False

def test_macro_analyzer():
    """매크로 분석기 테스트"""
    print(f"\n🧭 매크로 분석기 테스트")
    print("="*30)
    
    try:
        from coincompass.analysis.macro import MacroeconomicAnalyzer
        
        analyzer = MacroeconomicAnalyzer()
        print(f"📊 경제 지표 수집 테스트 중...")
        
        # 저장된 키로 경제 지표 수집
        indicators = analyzer.get_economic_indicators()
        
        if indicators:
            print(f"✅ 경제 지표 수집 성공!")
            
            # FRED 데이터 확인
            fred_found = False
            for key, value in indicators.items():
                if key in ['fed_rate', 'unemployment', 'cpi'] and isinstance(value, dict):
                    print(f"   📈 {key}: {value.get('value', 'N/A')}")
                    fred_found = True
            
            # 시장 데이터 확인
            if 'market_indices' in indicators:
                print(f"   💹 시장 데이터도 수집됨 ({len(indicators['market_indices'])}개)")
            
            return fred_found
        else:
            print(f"❌ 경제 지표 수집 실패")
            return False
            
    except Exception as e:
        print(f"❌ 매크로 분석기 오류: {str(e)}")
        return False

def show_usage_guide():
    """사용법 안내"""
    print(f"\n📋 CoinCompass FRED 활용 가이드")
    print("="*50)
    print(f"✅ FRED API 키 설정 완료!")
    print(f"")
    print(f"🚀 이제 다음과 같이 사용하세요:")
    print(f"")
    print(f"1️⃣ 종합 시장 분석:")
    print(f"   python3 run_coincompass.py")
    print(f"   → 메뉴 3번 선택")
    print(f"   → 저장된 FRED 키로 경제 지표 자동 분석")
    print(f"")
    print(f"2️⃣ API 키 관리:")
    print(f"   python3 run_coincompass.py")
    print(f"   → 메뉴 7번 선택")
    print(f"   → API 키 보기/테스트/삭제")
    print(f"")
    print(f"3️⃣ 활용 가능한 경제 지표:")
    print(f"   • 연방기금금리 (FEDFUNDS)")
    print(f"   • 실업률 (UNRATE)")
    print(f"   • 소비자물가지수 (CPIAUCSL)")
    print(f"   • GDP (GDP)")
    print(f"   • 10년 국채 수익률 (GS10)")
    print(f"   • VIX 지수 (VIXCLS)")
    print(f"")
    print(f"🔐 보안:")
    print(f"   • API 키는 암호화되어 ~/.coincompass/ 에 저장")
    print(f"   • 안전한 파일 권한 설정 (사용자만 접근)")

def main():
    """메인 실행"""
    print("🧭 CoinCompass FRED API 키 검증 도구")
    print("="*60)
    
    if FRED_API_KEY == "여기에_발급받은_FRED_API_키_입력":
        print("❌ API 키를 입력하지 않았습니다!")
        print("")
        print("📝 사용법:")
        print("1. 이 스크립트 파일을 텍스트 에디터로 열기")
        print("2. FRED_API_KEY = \"여기에_발급받은_FRED_API_키_입력\" 찾기")
        print("3. 발급받은 실제 API 키로 교체")
        print("4. 파일 저장 후 다시 실행")
        print("")
        print("💡 FRED API 키 발급:")
        print("   https://fred.stlouisfed.org/docs/api/api_key.html")
        return
    
    # 1. FRED API 검증
    print(f"1️⃣ FRED API 키 검증 중...")
    api_valid = test_fred_api_directly(FRED_API_KEY)
    
    if not api_valid:
        print(f"\n❌ API 키가 유효하지 않습니다.")
        print(f"💡 확인사항:")
        print(f"   • API 키가 정확한지 확인")
        print(f"   • 네트워크 연결 상태 확인")
        print(f"   • FRED 사이트에서 키 재발급 시도")
        return
    
    # 2. CoinCompass에 저장
    print(f"\n2️⃣ CoinCompass에 저장 중...")
    save_success = save_to_coincompass(FRED_API_KEY)
    
    if not save_success:
        print(f"⚠️ API 키는 유효하지만 저장에 실패했습니다.")
        return
    
    # 3. 매크로 분석기 테스트
    print(f"\n3️⃣ 매크로 분석기 테스트...")
    macro_success = test_macro_analyzer()
    
    # 결과 요약
    print(f"\n🎯 최종 결과")
    print("="*40)
    print(f"✅ FRED API 키 유효성: {'통과' if api_valid else '실패'}")
    print(f"✅ CoinCompass 저장: {'성공' if save_success else '실패'}")
    print(f"✅ 매크로 분석기 연동: {'성공' if macro_success else '실패'}")
    
    if api_valid and save_success:
        show_usage_guide()
    else:
        print(f"\n❌ 설정에 실패했습니다. 위의 오류를 확인하세요.")

if __name__ == "__main__":
    main()