import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

def create_demo_data():
    """데모용 샘플 데이터 생성"""
    coins = ['bitcoin', 'ethereum', 'ripple', 'solana', 'dogecoin']
    
    demo_data = {}
    base_time = datetime.now() - timedelta(hours=3)
    
    for coin in coins:
        history = []
        base_price = {'bitcoin': 117000, 'ethereum': 2950, 'ripple': 2.85, 'solana': 160, 'dogecoin': 0.19}[coin]
        
        for i in range(12):  # 3시간 동안 15분 간격
            timestamp = base_time + timedelta(minutes=15*i)
            
            # 랜덤 가격 변동 시뮬레이션
            price_change = np.random.normal(0, 0.02)  # 평균 0%, 표준편차 2%
            current_price = base_price * (1 + price_change)
            
            # RSI 시뮬레이션
            rsi = 30 + np.random.beta(2, 2) * 40  # 30-70 범위
            
            # 24시간 변동률 시뮬레이션
            change_24h = np.random.normal(0, 5)  # 평균 0%, 표준편차 5%
            
            data_point = {
                'timestamp': timestamp,
                'coin_id': coin,
                'price': current_price,
                'market_cap': current_price * np.random.uniform(19e6, 21e6),  # BTC 기준
                'volume_24h': np.random.uniform(1e9, 50e9),
                'price_change_24h': change_24h,
                'rsi': rsi,
                'sma_5': current_price * np.random.uniform(0.98, 1.02),
                'sma_20': current_price * np.random.uniform(0.95, 1.05)
            }
            
            history.append(data_point)
        
        demo_data[coin] = history
    
    return demo_data

def create_demo_price_chart(data_history):
    """데모 가격 차트 생성"""
    plt.figure(figsize=(15, 10))
    
    coins_to_plot = list(data_history.keys())[:5]
    
    for i, coin_id in enumerate(coins_to_plot):
        data = data_history[coin_id]
        df = pd.DataFrame(data)
        times = df['timestamp']
        prices = df['price']
        
        plt.subplot(2, 3, i+1)
        plt.plot(times, prices, marker='o', linewidth=2, markersize=4, color=plt.cm.tab10(i))
        plt.title(f'{coin_id.upper()} Price Trend', fontsize=12, fontweight='bold')
        plt.xlabel('Time')
        plt.ylabel('Price (USD)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # 최신 가격 표시
        latest_price = prices.iloc[-1]
        plt.text(times.iloc[-1], latest_price, f'${latest_price:,.2f}', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    # RSI 차트
    plt.subplot(2, 3, 6)
    for i, coin_id in enumerate(coins_to_plot):
        data = data_history[coin_id]
        df = pd.DataFrame(data)
        plt.plot(df['timestamp'], df['rsi'], marker='o', label=coin_id.upper(), 
                linewidth=2, color=plt.cm.tab10(i))
    
    plt.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Overbought')
    plt.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Oversold')
    plt.title('RSI Comparison', fontsize=12, fontweight='bold')
    plt.xlabel('Time')
    plt.ylabel('RSI')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # 차트 저장
    os.makedirs("charts", exist_ok=True)
    chart_filename = f"charts/demo_price_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
    plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    return chart_filename

def create_demo_market_overview(data_history):
    """데모 시장 개요 차트 생성"""
    # 최신 데이터만 사용
    latest_data = []
    for coin_id, history in data_history.items():
        if history:
            latest_data.append(history[-1])
    
    df = pd.DataFrame(latest_data)
    
    plt.figure(figsize=(16, 12))
    
    # 1. 시가총액 비교 (파이 차트)
    plt.subplot(2, 3, 1)
    market_caps = df['market_cap']
    labels = [coin.upper() for coin in df['coin_id']]
    colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
    
    plt.pie(market_caps, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    plt.title('Market Cap Distribution', fontsize=12, fontweight='bold')
    
    # 2. 24시간 가격 변동률
    plt.subplot(2, 3, 2)
    price_changes = df['price_change_24h']
    coin_names = [coin.upper() for coin in df['coin_id']]
    colors = ['green' if x > 0 else 'red' for x in price_changes]
    
    bars = plt.bar(coin_names, price_changes, color=colors, alpha=0.7)
    plt.title('24h Price Change (%)', fontsize=12, fontweight='bold')
    plt.xlabel('Coins')
    plt.ylabel('Change (%)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 값 표시
    for bar, value in zip(bars, price_changes):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (0.1 if value > 0 else -0.3), 
                f'{value:.1f}%', ha='center', fontweight='bold')
    
    # 3. RSI 분포
    plt.subplot(2, 3, 3)
    rsi_values = df['rsi']
    coin_names_rsi = [coin.upper() for coin in df['coin_id']]
    colors = ['red' if x > 70 else 'green' if x < 30 else 'gray' for x in rsi_values]
    
    bars = plt.bar(coin_names_rsi, rsi_values, color=colors, alpha=0.7)
    plt.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought')
    plt.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold')
    plt.title('Current RSI Values', fontsize=12, fontweight='bold')
    plt.xlabel('Coins')
    plt.ylabel('RSI')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # RSI 값 표시
    for bar, value in zip(bars, rsi_values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{value:.1f}', ha='center', fontweight='bold')
    
    # 4. 거래량 TOP 5
    plt.subplot(2, 3, 4)
    volumes = df['volume_24h'] / 1e9  # 10억 단위
    coin_names_vol = [coin.upper() for coin in df['coin_id']]
    
    bars = plt.bar(coin_names_vol, volumes, color='skyblue', alpha=0.8)
    plt.title('Trading Volume (24h)', fontsize=12, fontweight='bold')
    plt.xlabel('Coins')
    plt.ylabel('Volume (Billions USD)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 거래량 값 표시
    for bar, value in zip(bars, volumes):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'${value:.1f}B', ha='center', fontweight='bold')
    
    # 5. 가격 히트맵
    plt.subplot(2, 3, 5)
    price_matrix = []
    coin_labels = []
    
    for coin_id, history in data_history.items():
        recent_prices = [h['price'] for h in history[-6:]]  # 최근 6개 포인트
        # 정규화 (0-1 스케일)
        prices_norm = (np.array(recent_prices) - min(recent_prices)) / (max(recent_prices) - min(recent_prices))
        price_matrix.append(prices_norm)
        coin_labels.append(coin_id.upper())
    
    price_matrix = np.array(price_matrix)
    sns.heatmap(price_matrix, yticklabels=coin_labels, 
               xticklabels=[f'T-{i}' for i in range(len(price_matrix[0])-1, -1, -1)],
               cmap='RdYlGn', center=0.5, annot=False, cbar_kws={'label': 'Price Trend'})
    plt.title('Price Trend Heatmap', fontsize=12, fontweight='bold')
    plt.xlabel('Time Points (Recent to Past)')
    
    # 6. 종합 스코어
    plt.subplot(2, 3, 6)
    scores = []
    score_labels = []
    
    for _, row in df.iterrows():
        # 스코어 계산: RSI 중립성 + 가격 안정성
        rsi_score = 50 - abs(row['rsi'] - 50)  # RSI가 50에 가까울수록 높은 점수
        price_stability = max(0, 10 - abs(row['price_change_24h']))  # 변동성이 낮을수록 높은 점수
        total_score = (rsi_score + price_stability) / 2
        
        scores.append(total_score)
        score_labels.append(row['coin_id'].upper())
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(scores)))
    bars = plt.bar(score_labels, scores, color=colors, alpha=0.8)
    plt.title('Stability Score (RSI + Price)', fontsize=12, fontweight='bold')
    plt.xlabel('Coins')
    plt.ylabel('Score')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 점수 표시
    for bar, value in zip(bars, scores):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{value:.1f}', ha='center', fontweight='bold')
    
    plt.tight_layout()
    
    # 차트 저장
    chart_filename = f"charts/demo_market_overview_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
    plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    return chart_filename

def generate_demo_report(data_history):
    """데모 분석 보고서 생성"""
    latest_data = []
    for coin_id, history in data_history.items():
        if history:
            latest_data.append(history[-1])
    
    df = pd.DataFrame(latest_data)
    timestamp = datetime.now()
    
    report = f"""
🤖 TOP 5 코인 분석 보고서 (데모)
📅 생성시간: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

📊 시장 현황
• 총 {len(df)}개 코인 모니터링 중
• 평균 24h 변동률: {df['price_change_24h'].mean():.2f}%
• 상승 코인: {len(df[df['price_change_24h'] > 0])}개
• 하락 코인: {len(df[df['price_change_24h'] < 0])}개

🏆 TOP 퍼포머 (24h)
"""
    
    # 상위 3개 상승 코인
    top_gainers = df.nlargest(3, 'price_change_24h')
    for i, (_, coin) in enumerate(top_gainers.iterrows(), 1):
        report += f"{i}. {coin['coin_id'].upper()}: +{coin['price_change_24h']:.2f}% (${coin['price']:,.2f})\n"
    
    report += "\n📉 하락 코인 (24h)\n"
    
    # 하위 3개 하락 코인
    top_losers = df.nsmallest(3, 'price_change_24h')
    for i, (_, coin) in enumerate(top_losers.iterrows(), 1):
        report += f"{i}. {coin['coin_id'].upper()}: {coin['price_change_24h']:.2f}% (${coin['price']:,.2f})\n"
    
    # RSI 분석
    overbought = df[df['rsi'] > 70]
    oversold = df[df['rsi'] < 30]
    
    report += f"\n📈 기술적 분석 (RSI)\n"
    report += f"• 과매수 (RSI > 70): {len(overbought)}개 코인\n"
    if len(overbought) > 0:
        for _, coin in overbought.iterrows():
            report += f"  - {coin['coin_id'].upper()}: RSI {coin['rsi']:.1f}\n"
    
    report += f"• 과매도 (RSI < 30): {len(oversold)}개 코인\n"
    if len(oversold) > 0:
        for _, coin in oversold.iterrows():
            report += f"  - {coin['coin_id'].upper()}: RSI {coin['rsi']:.1f}\n"
    
    # 거래량 분석
    report += f"\n💰 거래량 TOP 3\n"
    top_volume = df.nlargest(3, 'volume_24h')
    for i, (_, coin) in enumerate(top_volume.iterrows(), 1):
        volume_b = coin['volume_24h'] / 1e9
        report += f"{i}. {coin['coin_id'].upper()}: ${volume_b:.1f}B\n"
    
    report += f"\n💡 투자 권장사항\n"
    
    # 안정적인 코인
    stable_coins = df[
        (abs(df['price_change_24h']) < 5) & 
        (df['rsi'] > 40) & 
        (df['rsi'] < 60)
    ]
    
    if len(stable_coins) > 0:
        report += "• 안정적 코인 (낮은 변동성):\n"
        for _, coin in stable_coins.head(3).iterrows():
            report += f"  - {coin['coin_id'].upper()}: 변동 {coin['price_change_24h']:+.1f}%, RSI {coin['rsi']:.1f}\n"
    
    # 주의 코인
    high_volatility = df[abs(df['price_change_24h']) > 10]
    if len(high_volatility) > 0:
        report += "• 고변동성 주의 코인:\n"
        for _, coin in high_volatility.iterrows():
            report += f"  - {coin['coin_id'].upper()}: {coin['price_change_24h']:+.1f}%\n"
    
    # 보고서 저장
    os.makedirs("reports", exist_ok=True)
    report_filename = f"reports/demo_analysis_report_{timestamp.strftime('%Y%m%d_%H%M')}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report, report_filename

def main():
    """데모 실행"""
    print("🎨 차트 생성 데모 실행 중...")
    
    # 샘플 데이터 생성
    demo_data = create_demo_data()
    
    # 차트 생성
    price_chart = create_demo_price_chart(demo_data)
    market_chart = create_demo_market_overview(demo_data)
    
    # 보고서 생성
    report, report_file = generate_demo_report(demo_data)
    
    print(f"\n✅ 데모 완료!")
    print(f"📈 가격 차트: {price_chart}")
    print(f"📊 시장 차트: {market_chart}")
    print(f"📋 보고서: {report_file}")
    
    print(f"\n{report}")

if __name__ == "__main__":
    main()