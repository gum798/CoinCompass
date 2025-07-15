import time
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from crypto_data import CoinGeckoAPI
from technical_indicators import TechnicalIndicators, TradingSignals
import matplotlib.pyplot as plt
import seaborn as sns
import os

class Top10Monitor:
    def __init__(self, interval_minutes=30):
        self.api = CoinGeckoAPI()
        self.interval_minutes = interval_minutes
        self.data_history = {}
        self.charts_dir = "charts"
        self.reports_dir = "reports"
        
        # 디렉토리 생성
        os.makedirs(self.charts_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # matplotlib 한글 폰트 설정
        plt.rcParams['font.family'] = ['Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
    def get_top10_coins(self):
        """시가총액 상위 10개 코인 조회"""
        top_coins = self.api.get_top_coins(10)
        if top_coins is not None:
            return top_coins['id'].tolist()
        return []
    
    def collect_coin_data(self, coin_id):
        """개별 코인 데이터 수집"""
        try:
            # 현재 가격 정보
            price_info = self.api.get_price(coin_id)
            if not price_info:
                return None
            
            current_data = price_info[coin_id]
            
            # 7일간 과거 데이터로 기술적 지표 계산
            historical = self.api.get_historical_data(coin_id, days=7)
            if historical is None:
                return None
            
            # RSI 계산
            rsi = TechnicalIndicators.calculate_rsi(historical['price']).iloc[-1]
            
            # 이동평균 계산
            sma_5 = TechnicalIndicators.calculate_sma(historical['price'], 5).iloc[-1]
            sma_20 = TechnicalIndicators.calculate_sma(historical['price'], 20).iloc[-1] if len(historical) >= 20 else None
            
            data = {
                'timestamp': datetime.now(),
                'coin_id': coin_id,
                'price': current_data['usd'],
                'market_cap': current_data.get('usd_market_cap', 0),
                'volume_24h': current_data.get('usd_24h_vol', 0),
                'price_change_24h': current_data.get('usd_24h_change', 0),
                'rsi': rsi if not np.isnan(rsi) else None,
                'sma_5': sma_5 if not np.isnan(sma_5) else None,
                'sma_20': sma_20 if sma_20 and not np.isnan(sma_20) else None
            }
            
            return data
            
        except Exception as e:
            print(f"❌ {coin_id} 데이터 수집 오류: {str(e)}")
            return None
    
    def update_history(self, coin_data):
        """데이터 히스토리 업데이트"""
        coin_id = coin_data['coin_id']
        
        if coin_id not in self.data_history:
            self.data_history[coin_id] = []
        
        self.data_history[coin_id].append(coin_data)
        
        # 최근 24시간 데이터만 유지 (48개 포인트)
        if len(self.data_history[coin_id]) > 48:
            self.data_history[coin_id] = self.data_history[coin_id][-48:]
    
    def create_price_chart(self, timestamp):
        """가격 차트 생성"""
        if not self.data_history:
            return None
            
        plt.figure(figsize=(15, 10))
        
        # 상위 5개 코인만 차트에 표시
        coins_to_plot = list(self.data_history.keys())[:5]
        
        for i, coin_id in enumerate(coins_to_plot):
            data = self.data_history[coin_id]
            if len(data) < 2:
                continue
                
            df = pd.DataFrame(data)
            times = df['timestamp']
            prices = df['price']
            
            plt.subplot(2, 3, i+1)
            plt.plot(times, prices, marker='o', linewidth=2, markersize=4)
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
        for coin_id in coins_to_plot:
            data = self.data_history[coin_id]
            if len(data) < 2:
                continue
                
            df = pd.DataFrame(data)
            df = df.dropna(subset=['rsi'])
            if len(df) > 0:
                plt.plot(df['timestamp'], df['rsi'], marker='o', label=coin_id.upper(), linewidth=2)
        
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
        chart_filename = f"{self.charts_dir}/top10_analysis_{timestamp.strftime('%Y%m%d_%H%M')}.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_filename
    
    def create_market_overview_chart(self, timestamp):
        """시장 개요 차트 생성"""
        if not self.data_history:
            return None
            
        # 최신 데이터만 사용
        latest_data = []
        for coin_id, history in self.data_history.items():
            if history:
                latest_data.append(history[-1])
        
        if not latest_data:
            return None
            
        df = pd.DataFrame(latest_data)
        
        plt.figure(figsize=(16, 12))
        
        # 1. 시가총액 비교 (파이 차트)
        plt.subplot(2, 3, 1)
        market_caps = df['market_cap'].head(8)
        labels = [coin.upper() for coin in df['coin_id'].head(8)]
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        plt.pie(market_caps, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        plt.title('Market Cap Distribution (Top 8)', fontsize=12, fontweight='bold')
        
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
        rsi_data = df.dropna(subset=['rsi'])
        if len(rsi_data) > 0:
            rsi_values = rsi_data['rsi']
            coin_names_rsi = [coin.upper() for coin in rsi_data['coin_id']]
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
        top_volume = df.nlargest(5, 'volume_24h')
        volumes = top_volume['volume_24h'] / 1e9  # 10억 단위
        coin_names_vol = [coin.upper() for coin in top_volume['coin_id']]
        
        bars = plt.bar(coin_names_vol, volumes, color='skyblue', alpha=0.8)
        plt.title('Top 5 Trading Volume (24h)', fontsize=12, fontweight='bold')
        plt.xlabel('Coins')
        plt.ylabel('Volume (Billions USD)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # 거래량 값 표시
        for bar, value in zip(bars, volumes):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    f'${value:.1f}B', ha='center', fontweight='bold')
        
        # 5. 가격 히트맵 (최근 데이터 포인트들)
        plt.subplot(2, 3, 5)
        price_matrix = []
        coin_labels = []
        
        for coin_id, history in list(self.data_history.items())[:8]:
            if len(history) >= 3:
                recent_prices = [h['price'] for h in history[-6:]]  # 최근 6개 포인트
                # 정규화 (0-1 스케일)
                prices_norm = (np.array(recent_prices) - min(recent_prices)) / (max(recent_prices) - min(recent_prices)) if max(recent_prices) != min(recent_prices) else [0.5] * len(recent_prices)
                price_matrix.append(prices_norm)
                coin_labels.append(coin_id.upper())
        
        if price_matrix:
            price_matrix = np.array(price_matrix)
            sns.heatmap(price_matrix, yticklabels=coin_labels, 
                       xticklabels=[f'T-{i}' for i in range(len(price_matrix[0])-1, -1, -1)],
                       cmap='RdYlGn', center=0.5, annot=False, cbar_kws={'label': 'Price Trend'})
            plt.title('Price Trend Heatmap', fontsize=12, fontweight='bold')
            plt.xlabel('Time Points (Recent to Past)')
        
        # 6. 종합 스코어 (RSI + 가격변동 기반)
        plt.subplot(2, 3, 6)
        scores = []
        score_labels = []
        
        for _, row in df.iterrows():
            if pd.notna(row['rsi']):
                # 스코어 계산: RSI 중립성 + 가격 안정성
                rsi_score = 50 - abs(row['rsi'] - 50)  # RSI가 50에 가까울수록 높은 점수
                price_stability = max(0, 10 - abs(row['price_change_24h']))  # 변동성이 낮을수록 높은 점수
                total_score = (rsi_score + price_stability) / 2
                
                scores.append(total_score)
                score_labels.append(row['coin_id'].upper())
        
        if scores:
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
        chart_filename = f"{self.charts_dir}/market_overview_{timestamp.strftime('%Y%m%d_%H%M')}.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_filename
    
    def generate_analysis_report(self, timestamp):
        """분석 보고서 생성"""
        if not self.data_history:
            return None
        
        # 최신 데이터 수집
        latest_data = []
        for coin_id, history in self.data_history.items():
            if history:
                latest_data.append(history[-1])
        
        if not latest_data:
            return None
        
        df = pd.DataFrame(latest_data)
        
        report = f"""
🤖 TOP 10 코인 분석 보고서
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
        df_rsi = df.dropna(subset=['rsi'])
        if len(df_rsi) > 0:
            overbought = df_rsi[df_rsi['rsi'] > 70]
            oversold = df_rsi[df_rsi['rsi'] < 30]
            
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
        
        # 투자 권장사항
        report += f"\n💡 투자 권장사항\n"
        
        # 안정적인 코인 (낮은 변동성 + 중립 RSI)
        if len(df_rsi) > 0:
            stable_coins = df_rsi[
                (abs(df_rsi['price_change_24h']) < 5) & 
                (df_rsi['rsi'] > 40) & 
                (df_rsi['rsi'] < 60)
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
        
        report += f"\n⏰ 다음 업데이트: {(timestamp + timedelta(minutes=self.interval_minutes)).strftime('%H:%M')}\n"
        
        # 보고서 저장
        report_filename = f"{self.reports_dir}/analysis_report_{timestamp.strftime('%Y%m%d_%H%M')}.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report, report_filename
    
    def run_single_analysis(self):
        """단일 분석 실행 (테스트용)"""
        print("🔄 TOP 10 코인 데이터 수집 중...")
        
        top_coins = self.get_top10_coins()
        if not top_coins:
            print("❌ TOP 10 코인 목록을 가져올 수 없습니다.")
            return
        
        print(f"📊 분석 대상: {', '.join([coin.upper() for coin in top_coins])}")
        
        timestamp = datetime.now()
        collected_data = []
        
        for i, coin_id in enumerate(top_coins):
            print(f"📈 {coin_id.upper()} 분석 중... ({i+1}/{len(top_coins)})")
            
            data = self.collect_coin_data(coin_id)
            if data:
                self.update_history(data)
                collected_data.append(data)
                rsi_text = f"{data['rsi']:.1f}" if data['rsi'] is not None else "N/A"
                print(f"  ✅ 가격: ${data['price']:,.2f}, RSI: {rsi_text}")
            else:
                print(f"  ❌ 데이터 수집 실패")
            
            # API 제한 고려
            time.sleep(1.2)
        
        if collected_data:
            print(f"\n📊 차트 생성 중...")
            
            # 차트 생성
            price_chart = self.create_price_chart(timestamp)
            market_chart = self.create_market_overview_chart(timestamp)
            
            # 보고서 생성
            report, report_file = self.generate_analysis_report(timestamp)
            
            print(f"\n✅ 분석 완료!")
            print(f"📈 가격 차트: {price_chart}")
            print(f"📊 시장 차트: {market_chart}")
            print(f"📋 보고서: {report_file}")
            
            print(f"\n{report}")
            
            return {
                'price_chart': price_chart,
                'market_chart': market_chart,
                'report': report,
                'report_file': report_file
            }
        
        return None
    
    def start_monitoring(self):
        """30분 간격 모니터링 시작"""
        print(f"🚀 TOP 10 코인 모니터링 시작 (간격: {self.interval_minutes}분)")
        
        try:
            while True:
                result = self.run_single_analysis()
                
                if result:
                    print(f"\n⏰ {self.interval_minutes}분 후 다음 분석...")
                else:
                    print(f"\n❌ 분석 실패. {self.interval_minutes}분 후 재시도...")
                
                time.sleep(self.interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 모니터링이 중단되었습니다.")

def main():
    monitor = Top10Monitor(interval_minutes=30)
    
    print("🎯 선택하세요:")
    print("1. 단일 분석 실행")
    print("2. 30분 간격 연속 모니터링")
    
    choice = input("선택 (1 또는 2): ").strip()
    
    if choice == "1":
        monitor.run_single_analysis()
    elif choice == "2":
        monitor.start_monitoring()
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()