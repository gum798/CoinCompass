"""
CoinCompass 기본 사용 예제
"""

import time
from coincompass import (
    DataManager, MultiAPIProvider, TechnicalAnalyzer, RealTimeMonitor,
    MarketAnalyzer, OnChainAnalyzer, MacroeconomicAnalyzer
)
from coincompass.utils.formatters import format_price, format_percentage
from coincompass.utils.logger import get_logger

logger = get_logger(__name__)

def basic_price_check():
    """기본 가격 조회 예제"""
    print("🧭 CoinCompass 기본 가격 조회 예제")
    print("="*50)
    
    # API 제공자 초기화
    api = MultiAPIProvider()
    
    # 비트코인 가격 조회
    print("\n📊 비트코인 가격 조회:")
    btc_data = api.get_price_data("bitcoin")
    
    if btc_data:
        print(f"💰 가격: {format_price(btc_data.price)}")
        print(f"📈 24h 변동: {format_percentage(btc_data.price_change_24h)}")
        print(f"📊 출처: {btc_data.source}")
    else:
        print("❌ 데이터 조회 실패")

def multi_coin_analysis():
    """여러 코인 분석 예제"""
    print("\n🔍 여러 코인 분석 예제")
    print("="*50)
    
    api = MultiAPIProvider()
    analyzer = TechnicalAnalyzer()
    
    coins = ["bitcoin", "ethereum", "ripple"]
    results = api.get_multiple_prices(coins)
    
    for coin_id, price_data in results.items():
        print(f"\n{coin_id.upper()}:")
        print(f"  가격: {format_price(price_data.price)}")
        print(f"  변동: {format_percentage(price_data.price_change_24h)}")
        print(f"  출처: {price_data.source}")

def monitoring_example():
    """모니터링 예제 (짧은 시간)"""
    print("\n⏰ 실시간 모니터링 예제 (30초)")
    print("="*50)
    
    # 설정 파일 없이 기본값으로 초기화
    monitor = RealTimeMonitor()
    
    # 짧은 테스트를 위해 설정 수정
    monitor.settings.monitoring.interval_seconds = 10
    monitor.settings.monitoring.coins = ["bitcoin", "ethereum"]
    
    print("모니터링을 시작합니다... (30초 후 자동 중지)")
    
    # 별도 스레드에서 30초 후 중지
    import threading
    def stop_after_delay():
        time.sleep(30)
        monitor.stop_monitoring()
    
    stop_thread = threading.Thread(target=stop_after_delay)
    stop_thread.start()
    
    # 모니터링 시작
    monitor.start_monitoring()
    
    print("모니터링이 완료되었습니다.")

def data_management_example():
    """데이터 관리 예제"""
    print("\n💾 데이터 관리 예제")
    print("="*50)
    
    data_manager = DataManager()
    
    # 샘플 데이터 저장
    sample_data = {
        "timestamp": "2025-07-15T12:00:00",
        "bitcoin_price": 117000,
        "ethereum_price": 2950
    }
    
    filename = data_manager.save_to_file(sample_data, "sample_data.json", "examples/data")
    print(f"✅ 데이터 저장: {filename}")
    
    # 데이터 로드
    loaded_data = data_manager.load_from_file(filename)
    print(f"📖 로드된 데이터: {loaded_data}")
    
    # 통계 조회
    stats = data_manager.get_data_stats()
    print(f"📊 데이터 관리 통계: {stats}")

def comprehensive_analysis_example():
    """종합 분석 예제"""
    print("\n🧭 종합 시장 분석 예제")
    print("="*50)
    
    analyzer = MarketAnalyzer()
    
    # 샘플 가격 데이터 생성
    import pandas as pd
    import numpy as np
    sample_prices = pd.Series(np.random.normal(100, 5, 50).cumsum())
    
    print("📊 비트코인 종합 분석 중...")
    analysis = analyzer.get_comprehensive_analysis("bitcoin", sample_prices)
    
    if analysis.get('summary'):
        summary = analysis['summary']
        print(f"\n🎯 분석 결과:")
        print(f"  추천: {summary['recommendation']}")
        print(f"  신뢰도: {summary['confidence']:.1%}")
        print(f"  종합점수: {summary['overall_score']:.2f}")
    
    # 시장 개요
    print(f"\n🌍 시장 개요:")
    overview = analyzer.get_market_overview(["bitcoin", "ethereum"])
    if overview.get('market_summary'):
        print(overview['market_summary'])

def onchain_analysis_example():
    """온체인 분석 예제"""
    print("\n🔗 온체인 분석 예제")
    print("="*50)
    
    onchain = OnChainAnalyzer()
    
    print("📊 블록체인 메트릭스 수집 중...")
    metrics = onchain.get_blockchain_metrics()
    
    if metrics.get('bitcoin'):
        btc = metrics['bitcoin']
        print(f"🟠 비트코인 네트워크:")
        print(f"  최신 블록: {btc.get('latest_block_height', 'N/A')}")
        print(f"  평균 블록시간: {btc.get('avg_block_time_seconds', 'N/A')}초")

def macro_analysis_example():
    """거시경제 분석 예제"""
    print("\n📈 거시경제 분석 예제")
    print("="*50)
    
    macro = MacroeconomicAnalyzer()
    
    print("📊 시장 데이터 수집 중...")
    indicators = macro.get_economic_indicators()
    
    if indicators.get('market_indices'):
        print("\n💹 주요 시장 지수:")
        for name, data in list(indicators['market_indices'].items())[:3]:
            print(f"  {name}: ${data['price']:.2f} ({data['change_1d']:+.2f}%)")

def main():
    """메인 실행 함수"""
    print("🧭 CoinCompass 예제 모음")
    print("="*60)
    
    try:
        # 1. 기본 가격 조회
        basic_price_check()
        
        # 2. 여러 코인 분석
        multi_coin_analysis()
        
        # 3. 데이터 관리
        data_management_example()
        
        # 4. 종합 분석
        comprehensive_analysis_example()
        
        # 5. 온체인 분석
        onchain_analysis_example()
        
        # 6. 거시경제 분석
        macro_analysis_example()
        
        # 7. 모니터링 (사용자 선택)
        response = input("\n실시간 모니터링을 테스트하시겠습니까? (y/N): ")
        if response.lower() == 'y':
            monitoring_example()
        
        print("\n✅ 모든 예제가 완료되었습니다!")
        
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"예제 실행 중 오류: {str(e)}")
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()