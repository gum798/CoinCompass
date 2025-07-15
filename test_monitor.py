from real_time_monitor import RealTimeMonitor
import time

def test_monitor():
    """모니터링 시스템 테스트 (1회만 실행)"""
    print("🧪 모니터링 시스템 테스트 중...")
    
    monitor = RealTimeMonitor()
    
    # 설정 확인
    print(f"모니터링 코인: {monitor.config['coins']}")
    print(f"RSI 임계값: {monitor.config['rsi_oversold']} ~ {monitor.config['rsi_overbought']}")
    print(f"가격 변동 임계값: {monitor.config['price_change_threshold']}%")
    print("-" * 50)
    
    # 각 코인 1회 체크
    for coin in monitor.config["coins"]:
        print(f"\n📊 {coin.upper()} 분석 중...")
        current_price, alerts = monitor.monitor_coin(coin)
        
        if current_price:
            print(f"💰 현재 가격: ${current_price:,.2f}")
            
            if alerts:
                print("🚨 알림:")
                for alert in alerts:
                    print(f"  - {alert}")
            else:
                print("✅ 특별한 신호 없음")
        else:
            print("❌ 데이터 조회 실패")
        
        # API 제한 고려
        time.sleep(1)
    
    print("\n✅ 테스트 완료!")
    print("실시간 모니터링을 시작하려면 'python real_time_monitor.py'를 실행하세요.")

if __name__ == "__main__":
    test_monitor()