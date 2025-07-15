#!/usr/bin/env python3
"""
CoinCompass 실행 스크립트
새로운 패키지 구조로 CoinCompass를 쉽게 실행할 수 있는 메인 스크립트
"""

import sys
import os
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from coincompass.api.multi_provider import MultiAPIProvider
from coincompass.analysis.technical import TechnicalAnalyzer
from coincompass.analysis.market_analyzer import MarketAnalyzer
from coincompass.analysis.price_driver import PriceDriverAnalyzer
from coincompass.analysis.backtesting import PriceDriverValidator
from coincompass.monitoring.real_time import RealTimeMonitor
from coincompass.visualization.enhanced_charts import EnhancedChartGenerator
from coincompass.reporting.validation_report import ValidationReportGenerator
from coincompass.config.api_keys import get_api_key_manager
from coincompass.utils.formatters import format_price, format_percentage
from coincompass.utils.logger import get_logger
import pandas as pd
import numpy as np

logger = get_logger(__name__)

def quick_price_check():
    """빠른 가격 체크"""
    print("🧭 CoinCompass - 빠른 가격 체크")
    print("="*50)
    
    api = MultiAPIProvider()
    coins = ["bitcoin", "ethereum", "ripple"]
    
    print("📊 주요 코인 현재 가격:")
    results = api.get_multiple_prices(coins, delay=1.0)
    
    for coin_id, price_data in results.items():
        print(f"💰 {coin_id.upper()}: {format_price(price_data.price)} "
              f"({format_percentage(price_data.price_change_24h)}) "
              f"[{price_data.source}]")
    
    # API 통계 출력
    api.print_stats()

def technical_analysis_demo():
    """기술적 분석 데모"""
    print("\n📈 기술적 분석 데모")
    print("="*50)
    
    api = MultiAPIProvider()
    analyzer = TechnicalAnalyzer()
    
    # 비트코인 분석
    print("🔍 비트코인 기술적 분석:")
    btc_data = api.get_price_data("bitcoin")
    
    if btc_data:
        # 샘플 가격 데이터 생성 (실제로는 과거 데이터 사용)
        sample_prices = pd.Series([
            btc_data.price * (1 + (i-10)*0.01) for i in range(20)
        ])
        
        indicators = analyzer.analyze_price_data(sample_prices)
        signal = analyzer.generate_trading_signal(sample_prices, indicators)
        
        print(f"  현재가: {format_price(btc_data.price)}")
        print(f"  RSI: {indicators.rsi:.1f}" if indicators.rsi else "  RSI: N/A")
        print(f"  MACD: {indicators.macd:.2f}" if indicators.macd else "  MACD: N/A")
        print(f"  매매신호: {signal.signal} (신뢰도: {signal.confidence:.1%})")
        print(f"  근거: {signal.reason}")

def start_monitoring():
    """실시간 모니터링 시작"""
    print("\n⏰ 실시간 모니터링 시작")
    print("="*50)
    print("Ctrl+C로 중단할 수 있습니다")
    
    try:
        monitor = RealTimeMonitor()
        
        # 테스트용 짧은 간격 설정
        monitor.settings.monitoring.interval_seconds = 30
        monitor.settings.monitoring.coins = ["bitcoin", "ethereum"]
        
        print(f"📋 모니터링 코인: {', '.join(monitor.settings.get_coins_list())}")
        print(f"⏱️  체크 간격: {monitor.settings.monitoring.interval_seconds}초")
        
        monitor.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n🛑 모니터링이 중단되었습니다")

def comprehensive_market_analysis():
    """종합 시장 분석"""
    print("\n📊 종합 시장 분석")
    print("="*50)
    
    analyzer = MarketAnalyzer()
    api = MultiAPIProvider()
    
    # 비트코인 데이터로 분석
    print("🔍 비트코인 종합 분석 중...")
    btc_data = api.get_price_data("bitcoin")
    
    if btc_data:
        # 샘플 가격 데이터 생성 (실제로는 과거 데이터 사용)
        sample_prices = pd.Series([
            btc_data.price * (1 + (i-20)*0.005) for i in range(40)
        ])
        
        # 저장된 FRED API 키 확인
        api_manager = get_api_key_manager()
        stored_fred_key = api_manager.load_api_key('fred')
        
        if stored_fred_key:
            print(f"✅ 저장된 FRED API 키 사용")
            fred_key = stored_fred_key
        else:
            fred_key = input("\nFRED API 키를 입력하세요 (없으면 Enter): ").strip()
            fred_key = fred_key if fred_key else None
        
        analysis = analyzer.get_comprehensive_analysis("bitcoin", sample_prices, fred_key)
        
        # 결과 출력
        if analysis.get('summary'):
            summary = analysis['summary']
            print(f"\n🎯 종합 분석 결과:")
            print(f"  현재가: {format_price(btc_data.price)}")
            print(f"  추천: {summary['recommendation']}")
            print(f"  신뢰도: {summary['confidence']:.1%}")
            print(f"  종합점수: {summary['overall_score']:.2f}/1.00")
            
            if summary['key_factors']:
                print(f"\n✅ 주요 긍정 요인:")
                for factor in summary['key_factors']:
                    print(f"  • {factor}")
            
            if summary['opportunities']:
                print(f"\n🚀 기회 요인:")
                for opp in summary['opportunities']:
                    print(f"  • {opp}")
            
            if summary['risks']:
                print(f"\n⚠️ 위험 요인:")
                for risk in summary['risks']:
                    print(f"  • {risk}")
        
        # 시장 전체 개요
        print(f"\n🌍 시장 전체 개요:")
        market_overview = analyzer.get_market_overview(["bitcoin", "ethereum"], fred_key)
        
        if market_overview.get('market_summary'):
            print(market_overview['market_summary'])
    else:
        print("❌ 비트코인 데이터 조회 실패")

def price_movement_analysis():
    """가격 변동 요인 분석 및 차트"""
    print("\n📊 가격 변동 요인 분석")
    print("="*50)
    
    api = MultiAPIProvider()
    analyzer = PriceDriverAnalyzer()
    chart_gen = EnhancedChartGenerator()
    
    # 코인 선택
    coin_options = ["bitcoin", "ethereum", "ripple"]
    print("분석할 코인을 선택하세요:")
    for i, coin in enumerate(coin_options, 1):
        print(f"{i}. {coin.upper()}")
    
    try:
        choice = input("\n선택 (1-3): ").strip()
        coin_id = coin_options[int(choice) - 1]
    except (ValueError, IndexError):
        coin_id = "bitcoin"
        print("기본값으로 비트코인을 선택합니다.")
    
    print(f"\n🔍 {coin_id.upper()} 가격 변동 분석 중...")
    
    # 현재 가격 데이터 조회
    current_data = api.get_price_data(coin_id)
    if not current_data:
        print("❌ 가격 데이터 조회 실패")
        return
    
    # 24시간 전 가격 시뮬레이션 (실제로는 과거 데이터 API 사용)
    # 변동률 시뮬레이션: -20% ~ +20% 랜덤
    np.random.seed()  # 매번 다른 결과
    change_percent = np.random.uniform(-20, 20)
    price_24h_ago = current_data.price / (1 + change_percent/100)
    
    # 가격 데이터 시뮬레이션 (48개 데이터 포인트, 30분 간격)
    price_data = pd.Series([
        price_24h_ago + (current_data.price - price_24h_ago) * (i/47) + 
        np.random.normal(0, current_data.price * 0.005)  # 노이즈 추가
        for i in range(48)
    ])
    
    print(f"💰 현재가: {format_price(current_data.price)}")
    print(f"📅 24h 전: {format_price(price_24h_ago)}")
    print(f"📊 변동률: {format_percentage(change_percent)}")
    
    # 가격 변동 분석
    analysis = analyzer.analyze_price_movement(
        coin_id=coin_id,
        current_price=current_data.price,
        price_24h_ago=price_24h_ago,
        price_data=price_data
    )
    
    # 분석 결과 출력
    print(f"\n🎯 분석 결과:")
    print(f"  변동 유형: {analysis.movement_type}")
    print(f"  변동률: {analysis.price_change_percent:+.2f}%")
    
    print(f"\n📝 요약:")
    print(f"  {analysis.summary}")
    
    if analysis.primary_factors:
        print(f"\n🔍 주요 변동 요인:")
        for i, factor in enumerate(analysis.primary_factors, 1):
            print(f"  {i}. {factor.description}")
            print(f"     영향도: {factor.impact_score:+.2f}, 신뢰도: {factor.confidence:.1%}")
    
    print(f"\n💡 투자 추천:")
    print(f"  {analysis.recommendation}")
    
    # 차트 생성 옵션
    create_chart = input(f"\n📊 상세 분석 차트를 생성하시겠습니까? (y/N): ").strip().lower()
    if create_chart == 'y':
        try:
            chart_path = f"reports/{coin_id}_price_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
            
            # 차트 생성
            chart_gen.create_price_analysis_chart(
                coin_id=coin_id,
                price_data=price_data,
                current_price=current_data.price,
                price_24h_ago=price_24h_ago,
                save_path=chart_path
            )
            print(f"✅ 차트 저장: {chart_path}")
            
        except Exception as e:
            logger.error(f"차트 생성 오류: {str(e)}")
            print(f"❌ 차트 생성 실패: {str(e)}")

def validation_report_generation():
    """검증 보고서 생성"""
    print("\n📋 가격 변동 분석 검증 보고서")
    print("="*50)
    
    validator = PriceDriverValidator()
    reporter = ValidationReportGenerator()
    
    # 코인 선택
    coin_options = ["bitcoin", "ethereum", "ripple"]
    print("검증할 코인을 선택하세요:")
    for i, coin in enumerate(coin_options, 1):
        print(f"{i}. {coin.upper()}")
    
    try:
        choice = input("\n선택 (1-3): ").strip()
        coin_id = coin_options[int(choice) - 1]
    except (ValueError, IndexError):
        coin_id = "bitcoin"
        print("기본값으로 비트코인을 선택합니다.")
    
    # 검증 기간 선택
    print(f"\n검증 기간을 선택하세요:")
    print("1. 7일 (빠른 검증)")
    print("2. 14일 (권장)")
    print("3. 30일 (정밀 검증)")
    
    try:
        period_choice = input("\n선택 (1-3): ").strip()
        days_options = {1: 7, 2: 14, 3: 30}
        days = days_options.get(int(period_choice), 14)
    except (ValueError, KeyError):
        days = 14
        print("기본값으로 14일을 선택합니다.")
    
    print(f"\n🔍 {coin_id.upper()} {days}일 검증 시작...")
    print("⏰ 과거 데이터 수집 및 분석 중... (1-2분 소요)")
    
    try:
        # 간단한 백테스팅 먼저 수행
        print("📊 백테스팅 수행 중...")
        report = validator.validate_price_predictions(coin_id, days)
        
        # 결과 요약 출력
        print(f"\n🎯 검증 결과 요약:")
        print(f"  전체 정확도: {report.accuracy_rate:.1%}")
        print(f"  총 예측 횟수: {report.total_predictions}")
        print(f"  정확한 예측: {report.correct_predictions}")
        
        if report.movement_type_accuracy:
            print(f"\n📈 변동 유형별 정확도:")
            for movement, accuracy in list(report.movement_type_accuracy.items())[:3]:
                print(f"    {movement}: {accuracy:.1%}")
        
        if report.factor_effectiveness:
            print(f"\n🔍 주요 효과 요인:")
            sorted_factors = sorted(report.factor_effectiveness.items(), 
                                  key=lambda x: x[1], reverse=True)
            for factor, effectiveness in sorted_factors[:3]:
                print(f"    {factor}: {effectiveness:.1%}")
        
        # 상세 보고서 생성 여부 확인
        create_detailed = input(f"\n📊 상세 검증 보고서를 생성하시겠습니까? (y/N): ").strip().lower()
        if create_detailed == 'y':
            report_path = f"reports/{coin_id}_validation_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
            
            print("📋 상세 검증 보고서 생성 중...")
            result_path = reporter.generate_comprehensive_validation_report(
                coin_id=coin_id,
                days=days,
                save_path=report_path
            )
            print(f"✅ 상세 보고서 저장: {result_path}")
            
            # 텍스트 보고서 경로도 알려주기
            text_path = report_path.replace('.png', '_report.txt')
            print(f"📄 텍스트 보고서: {text_path}")
        
        # 성능 평가 및 권장사항
        print(f"\n💡 종합 평가:")
        if report.accuracy_rate >= 0.7:
            print("  ✅ 우수한 성능! 분석 시스템이 신뢰할 만합니다.")
        elif report.accuracy_rate >= 0.5:
            print("  ⚠️ 적당한 성능. 참고용으로 활용하세요.")
        else:
            print("  ❌ 성능 개선 필요. 추가 데이터나 알고리즘 개선이 필요합니다.")
            
    except Exception as e:
        logger.error(f"검증 보고서 생성 오류: {str(e)}")
        print(f"❌ 검증 실패: {str(e)}")
        print("💡 인터넷 연결 또는 API 접근 권한을 확인해주세요.")

def api_key_management():
    """API 키 관리"""
    print("\n🔐 API 키 관리")
    print("="*50)
    
    api_manager = get_api_key_manager()
    
    while True:
        print("\n🔑 API 키 관리 메뉴:")
        print("1. FRED API 키 저장")
        print("2. 저장된 API 키 목록 보기")
        print("3. API 키 삭제")
        print("4. FRED API 키 테스트")
        print("0. 뒤로가기")
        print("-" * 30)
        
        try:
            choice = input("선택하세요 (0-4): ").strip()
            
            if choice == "1":
                # FRED API 키 저장
                print("\n📝 FRED API 키 저장")
                print("FRED API 키는 https://fred.stlouisfed.org/docs/api/api_key.html 에서 발급받을 수 있습니다.")
                api_key = input("FRED API 키를 입력하세요: ").strip()
                
                if api_key:
                    success = api_manager.save_api_key('fred', api_key)
                    if success:
                        print("✅ FRED API 키가 안전하게 저장되었습니다!")
                    else:
                        print("❌ API 키 저장에 실패했습니다.")
                else:
                    print("❌ API 키가 입력되지 않았습니다.")
            
            elif choice == "2":
                # 저장된 API 키 목록
                print("\n📋 저장된 API 키 목록:")
                services = api_manager.list_services()
                if services:
                    for i, service in enumerate(services, 1):
                        # API 키 일부만 표시 (보안상)
                        api_key = api_manager.load_api_key(service)
                        if api_key and len(api_key) > 8:
                            masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
                        else:
                            masked_key = "****"
                        print(f"  {i}. {service.upper()}: {masked_key}")
                else:
                    print("  저장된 API 키가 없습니다.")
            
            elif choice == "3":
                # API 키 삭제
                print("\n🗑️ API 키 삭제")
                services = api_manager.list_services()
                if services:
                    print("삭제할 API 키를 선택하세요:")
                    for i, service in enumerate(services, 1):
                        print(f"  {i}. {service.upper()}")
                    
                    try:
                        del_choice = input("선택 (번호 입력): ").strip()
                        service_to_delete = services[int(del_choice) - 1]
                        
                        confirm = input(f"정말로 {service_to_delete.upper()} API 키를 삭제하시겠습니까? (y/N): ").strip().lower()
                        if confirm == 'y':
                            success = api_manager.delete_api_key(service_to_delete)
                            if success:
                                print(f"✅ {service_to_delete.upper()} API 키가 삭제되었습니다.")
                            else:
                                print("❌ API 키 삭제에 실패했습니다.")
                        else:
                            print("❌ 삭제가 취소되었습니다.")
                    
                    except (ValueError, IndexError):
                        print("❌ 잘못된 선택입니다.")
                else:
                    print("  삭제할 API 키가 없습니다.")
            
            elif choice == "4":
                # FRED API 키 테스트
                print("\n🧪 FRED API 키 테스트")
                fred_key = api_manager.load_api_key('fred')
                
                if not fred_key:
                    print("❌ 저장된 FRED API 키가 없습니다.")
                    continue
                
                print("📊 FRED API 연결 테스트 중...")
                
                try:
                    # MacroeconomicAnalyzer를 임포트해서 테스트
                    from coincompass.analysis.macro import MacroeconomicAnalyzer
                    analyzer = MacroeconomicAnalyzer()
                    
                    # 간단한 지표 하나 테스트 (연방기금금리)
                    test_data = analyzer.get_fred_data('FEDFUNDS', fred_key, 7)
                    
                    if test_data:
                        print(f"✅ FRED API 연결 성공!")
                        print(f"  테스트 데이터: 연방기금금리 {test_data['value']}% ({test_data['date']})")
                    else:
                        print("❌ FRED API 연결 실패. API 키가 유효하지 않을 수 있습니다.")
                
                except Exception as e:
                    print(f"❌ FRED API 테스트 오류: {str(e)}")
            
            elif choice == "0":
                break
            
            else:
                print("❌ 잘못된 선택입니다. 0-4 중에서 선택하세요.")
                
        except KeyboardInterrupt:
            print("\n🔙 API 키 관리를 종료합니다.")
            break
        except Exception as e:
            logger.error(f"API 키 관리 오류: {str(e)}")
            print(f"❌ 오류 발생: {str(e)}")

def show_menu():
    """메뉴 표시"""
    print("\n🧭 CoinCompass 메뉴")
    print("="*30)
    print("1. 빠른 가격 체크")
    print("2. 기술적 분석 데모")
    print("3. 종합 시장 분석")
    print("4. 가격 변동 요인 분석")
    print("5. 검증 보고서 생성")
    print("6. 실시간 모니터링")
    print("7. API 키 관리 🔐")
    print("8. 예제 실행")
    print("0. 종료")
    print("="*30)

def run_examples():
    """예제 실행"""
    print("\n📚 예제 실행")
    print("="*50)
    
    try:
        # examples 모듈 임포트
        sys.path.append(os.path.join(current_dir, 'examples'))
        import basic_usage
        basic_usage.main()
    except Exception as e:
        print(f"❌ 예제 실행 오류: {str(e)}")

def main():
    """메인 함수"""
    print("🧭 CoinCompass v1.0")
    print("스마트 암호화폐 투자 나침반")
    print("GitHub: https://github.com/gum798/CoinCompass")
    
    while True:
        try:
            show_menu()
            choice = input("\n선택하세요 (0-8): ").strip()
            
            if choice == "1":
                quick_price_check()
            elif choice == "2":
                technical_analysis_demo()
            elif choice == "3":
                comprehensive_market_analysis()
            elif choice == "4":
                price_movement_analysis()
            elif choice == "5":
                validation_report_generation()
            elif choice == "6":
                start_monitoring()
            elif choice == "7":
                api_key_management()
            elif choice == "8":
                run_examples()
            elif choice == "0":
                print("👋 CoinCompass를 종료합니다")
                break
            else:
                print("❌ 잘못된 선택입니다. 0-8 중에서 선택하세요.")
                
        except KeyboardInterrupt:
            print("\n👋 CoinCompass를 종료합니다")
            break
        except Exception as e:
            logger.error(f"실행 중 오류: {str(e)}")
            print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()