from crypto_data import CoinGeckoAPI
from technical_indicators import analyze_coin, print_latest_analysis
import time

def main():
    """메인 실행 함수"""
    api = CoinGeckoAPI()
    
    print("🤖 코인 투자봇 프로토타입 v1.0")
    print("=" * 50)
    
    # 분석할 코인 리스트
    coins = ["bitcoin", "ethereum", "ripple"]
    
    for coin in coins:
        print(f"\n📊 {coin.upper()} 분석 중...")
        
        # 30일간 데이터 수집
        price_data = api.get_historical_data(coin, days=30)
        
        if price_data is not None:
            # 기술적 분석 수행
            analysis = analyze_coin(price_data, coin)
            
            # 결과 출력
            print_latest_analysis(analysis, coin)
        else:
            print(f"❌ {coin} 데이터를 가져올 수 없습니다.")
        
        # API 호출 제한을 위한 대기
        time.sleep(1)

if __name__ == "__main__":
    main()