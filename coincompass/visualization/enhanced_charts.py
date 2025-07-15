"""
향상된 차트 시각화 모듈
가격 변동 요인과 설명이 포함된 차트 생성
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

from ..analysis.price_driver import PriceDriverAnalyzer, PriceMovementAnalysis
from ..analysis.technical import TechnicalAnalyzer
from ..utils.logger import get_logger

logger = get_logger(__name__)

class EnhancedChartGenerator:
    """향상된 차트 생성기"""
    
    def __init__(self):
        self.price_analyzer = PriceDriverAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        
        # 한글 폰트 설정
        plt.rcParams['font.family'] = ['AppleGothic', 'Malgun Gothic', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 색상 테마
        self.colors = {
            'background': '#1e1e1e',
            'text': '#ffffff',
            'grid': '#404040',
            'up': '#26a69a',
            'down': '#ef5350',
            'neutral': '#90a4ae',
            'highlight': '#ffeb3b',
            'factor_bg': '#2d2d2d'
        }
    
    def create_price_analysis_chart(self, coin_id: str, price_data: pd.Series, 
                                  current_price: float, price_24h_ago: float,
                                  save_path: Optional[str] = None,
                                  fred_api_key: Optional[str] = None) -> str:
        """가격 분석이 포함된 종합 차트 생성"""
        
        logger.info(f"📊 {coin_id} 가격 분석 차트 생성 중...")
        
        # 가격 변동 분석
        analysis = self.price_analyzer.analyze_price_movement(
            coin_id=coin_id,
            current_price=current_price,
            price_24h_ago=price_24h_ago,
            price_data=price_data,
            fred_api_key=fred_api_key
        )
        
        # 기술적 지표 계산
        indicators = self.technical_analyzer.analyze_price_data(price_data)
        
        # 차트 생성
        fig = plt.figure(figsize=(16, 12))
        fig.patch.set_facecolor(self.colors['background'])
        
        # 그리드 설정
        gs = fig.add_gridspec(4, 3, height_ratios=[3, 1, 1, 1.5], width_ratios=[2, 1, 1])
        
        # 1. 메인 가격 차트
        ax_main = fig.add_subplot(gs[0, :])
        self._plot_main_price_chart(ax_main, price_data, current_price, analysis)
        
        # 2. RSI 차트
        ax_rsi = fig.add_subplot(gs[1, :])
        self._plot_rsi_chart(ax_rsi, price_data, indicators)
        
        # 3. MACD 차트
        ax_macd = fig.add_subplot(gs[2, :])
        self._plot_macd_chart(ax_macd, price_data, indicators)
        
        # 4. 변동 요인 분석 패널
        ax_factors = fig.add_subplot(gs[3, :])
        self._plot_factors_panel(ax_factors, analysis)
        
        # 전체 제목
        title = f"🧭 {coin_id.upper()} 가격 분석 ({analysis.price_change_percent:+.2f}%)"
        fig.suptitle(title, fontsize=20, color=self.colors['text'], fontweight='bold', y=0.98)
        
        # 레이아웃 조정
        plt.tight_layout()
        plt.subplots_adjust(top=0.95, hspace=0.3)
        
        # 저장
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                       facecolor=self.colors['background'], edgecolor='none')
            logger.info(f"💾 차트 저장: {save_path}")
        
        plt.show()
        return save_path or "chart_displayed"
    
    def _plot_main_price_chart(self, ax, price_data: pd.Series, current_price: float, 
                              analysis: PriceMovementAnalysis):
        """메인 가격 차트 그리기"""
        
        # X축 데이터 생성 (최근 24시간)
        times = pd.date_range(end=datetime.now(), periods=len(price_data), freq='30min')
        
        # 가격 선 그리기
        color = self.colors['up'] if analysis.price_change_percent > 0 else self.colors['down']
        ax.plot(times, price_data, linewidth=2.5, color=color, alpha=0.8)
        
        # 현재 가격 포인트 강조
        ax.scatter(times[-1], current_price, color=self.colors['highlight'], 
                  s=100, zorder=10, edgecolor='white', linewidth=2)
        
        # 가격 변동 구간 하이라이트
        if abs(analysis.price_change_percent) > 5:
            ax.fill_between(times, price_data, alpha=0.2, color=color)
        
        # 24시간 전 가격 표시
        start_price = price_data.iloc[0]
        ax.axhline(y=start_price, color=self.colors['neutral'], 
                  linestyle='--', alpha=0.7, linewidth=1)
        
        # 가격 정보 텍스트
        price_info = f"현재: ${current_price:,.0f}\n"
        price_info += f"24h 변동: {analysis.price_change_percent:+.2f}%\n"
        price_info += f"변동 유형: {self._get_movement_emoji(analysis.movement_type)}"
        
        ax.text(0.02, 0.98, price_info, transform=ax.transAxes, 
                fontsize=12, color=self.colors['text'], 
                bbox=dict(boxstyle='round,pad=0.5', facecolor=self.colors['factor_bg'], alpha=0.8),
                verticalalignment='top')
        
        # 축 설정
        ax.set_facecolor(self.colors['background'])
        ax.tick_params(colors=self.colors['text'])
        ax.spines['bottom'].set_color(self.colors['grid'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.colors['grid'])
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        
        # X축 포맷
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
        
        # Y축 레이블
        ax.set_ylabel('가격 (USD)', color=self.colors['text'], fontweight='bold')
        
        # 제목
        ax.set_title('📈 가격 추이 (24시간)', color=self.colors['text'], 
                    fontsize=14, fontweight='bold', pad=20)
    
    def _plot_rsi_chart(self, ax, price_data: pd.Series, indicators):
        """RSI 차트 그리기"""
        
        if not indicators or not indicators.rsi:
            ax.text(0.5, 0.5, 'RSI 데이터 없음', ha='center', va='center',
                   transform=ax.transAxes, color=self.colors['text'])
            return
        
        times = pd.date_range(end=datetime.now(), periods=len(price_data), freq='30min')
        
        # RSI 값 계산 (단순화된 버전)
        rsi_values = [indicators.rsi] * len(price_data)  # 실제로는 전체 기간 RSI 계산 필요
        
        # RSI 선 그리기
        color = self.colors['up'] if indicators.rsi > 50 else self.colors['down']
        ax.plot(times, rsi_values, color=color, linewidth=2)
        
        # 과매수/과매도 구간 표시
        ax.axhline(y=70, color=self.colors['down'], linestyle='--', alpha=0.7)
        ax.axhline(y=30, color=self.colors['up'], linestyle='--', alpha=0.7)
        ax.fill_between(times, 70, 100, alpha=0.1, color=self.colors['down'])
        ax.fill_between(times, 0, 30, alpha=0.1, color=self.colors['up'])
        
        # RSI 값 표시
        ax.text(0.02, 0.95, f'RSI: {indicators.rsi:.1f}', transform=ax.transAxes,
                fontsize=11, color=self.colors['text'], fontweight='bold')
        
        # 축 설정
        ax.set_facecolor(self.colors['background'])
        ax.tick_params(colors=self.colors['text'])
        ax.set_ylim(0, 100)
        ax.set_ylabel('RSI', color=self.colors['text'])
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        
        # 스파인 설정
        for spine in ax.spines.values():
            spine.set_color(self.colors['grid'])
    
    def _plot_macd_chart(self, ax, price_data: pd.Series, indicators):
        """MACD 차트 그리기"""
        
        if not indicators or not indicators.macd:
            ax.text(0.5, 0.5, 'MACD 데이터 없음', ha='center', va='center',
                   transform=ax.transAxes, color=self.colors['text'])
            return
        
        times = pd.date_range(end=datetime.now(), periods=len(price_data), freq='30min')
        
        # MACD 값 (단순화된 버전)
        macd_values = [indicators.macd] * len(price_data)
        signal_values = [indicators.macd_signal] * len(price_data) if indicators.macd_signal else [0] * len(price_data)
        
        # MACD 라인
        ax.plot(times, macd_values, color=self.colors['up'], linewidth=2, label='MACD')
        ax.plot(times, signal_values, color=self.colors['down'], linewidth=1.5, label='Signal')
        
        # 히스토그램
        histogram = [indicators.macd - (indicators.macd_signal or 0)] * len(price_data)
        colors = [self.colors['up'] if h >= 0 else self.colors['down'] for h in histogram]
        ax.bar(times, histogram, color=colors, alpha=0.6, width=0.02)
        
        # MACD 정보
        macd_info = f"MACD: {indicators.macd:.3f}"
        if indicators.macd_signal:
            macd_info += f"\nSignal: {indicators.macd_signal:.3f}"
        
        ax.text(0.02, 0.95, macd_info, transform=ax.transAxes,
                fontsize=11, color=self.colors['text'], fontweight='bold')
        
        # 축 설정
        ax.set_facecolor(self.colors['background'])
        ax.tick_params(colors=self.colors['text'])
        ax.set_ylabel('MACD', color=self.colors['text'])
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        ax.legend(loc='upper right', facecolor=self.colors['factor_bg'], 
                 edgecolor=self.colors['grid'])
        
        # 스파인 설정
        for spine in ax.spines.values():
            spine.set_color(self.colors['grid'])
    
    def _plot_factors_panel(self, ax, analysis: PriceMovementAnalysis):
        """변동 요인 분석 패널 그리기"""
        
        ax.set_facecolor(self.colors['background'])
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        
        # 축 숨기기
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # 제목
        ax.text(5, 9.5, '🔍 가격 변동 요인 분석', ha='center', va='top',
                fontsize=16, color=self.colors['text'], fontweight='bold')
        
        # 요약 설명
        summary_lines = analysis.summary.split('\n')
        y_pos = 8.5
        for line in summary_lines[:2]:  # 처음 2줄만
            ax.text(5, y_pos, line, ha='center', va='top',
                   fontsize=12, color=self.colors['text'])
            y_pos -= 0.5
        
        # 주요 요인들 표시
        if analysis.primary_factors:
            y_pos = 6.5
            
            for i, factor in enumerate(analysis.primary_factors[:2]):  # 상위 2개 요인
                # 요인 타입 아이콘
                factor_icons = {
                    'technical': '📊',
                    'sentiment': '😰', 
                    'macro': '🌍',
                    'structural': '🏗️'
                }
                icon = factor_icons.get(factor.factor_type, '📈')
                
                # 영향도 바
                impact_color = self.colors['up'] if factor.impact_score > 0 else self.colors['down']
                bar_width = abs(factor.impact_score) * 2  # 최대 2 단위
                
                ax.barh(y_pos, bar_width, height=0.3, color=impact_color, alpha=0.7)
                
                # 요인 설명
                factor_text = f"{icon} {factor.description[:50]}..."
                ax.text(0.2, y_pos + 0.15, factor_text, va='center',
                       fontsize=10, color=self.colors['text'])
                
                # 신뢰도 표시
                confidence_text = f"신뢰도: {factor.confidence:.0%}"
                ax.text(9.8, y_pos + 0.15, confidence_text, va='center', ha='right',
                       fontsize=9, color=self.colors['neutral'])
                
                y_pos -= 1.2
        
        # 투자 추천
        recommendation_color = self.colors['highlight']
        ax.text(5, 2, f"💡 {analysis.recommendation}", ha='center', va='center',
                fontsize=11, color=recommendation_color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor=self.colors['factor_bg'], alpha=0.8))
    
    def _get_movement_emoji(self, movement_type: str) -> str:
        """변동 유형에 따른 이모지 반환"""
        emojis = {
            'crash': '💥 급락',
            'dump': '📉 큰폭 하락',
            'normal_down': '📉 하락',
            'stable': '💤 횡보',
            'normal_up': '📈 상승',
            'pump': '📈 큰폭 상승',
            'surge': '🚀 급등'
        }
        return emojis.get(movement_type, '📊 변동')
    
    def create_simple_factor_chart(self, coin_id: str, price_change: float, 
                                 factors: List, save_path: Optional[str] = None) -> str:
        """간단한 요인 분석 차트"""
        
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor(self.colors['background'])
        ax.set_facecolor(self.colors['background'])
        
        # 제목
        title = f"📊 {coin_id.upper()} 가격 변동 요인 ({price_change:+.2f}%)"
        ax.text(0.5, 0.95, title, ha='center', va='top', transform=ax.transAxes,
                fontsize=18, color=self.colors['text'], fontweight='bold')
        
        # 요인별 막대 그래프
        if factors:
            factor_names = [f"{f.factor_type}" for f in factors]
            impact_scores = [f.impact_score for f in factors]
            
            colors = [self.colors['up'] if score > 0 else self.colors['down'] for score in impact_scores]
            
            bars = ax.barh(factor_names, impact_scores, color=colors, alpha=0.8)
            
            # 각 요인 설명 추가
            for i, (bar, factor) in enumerate(zip(bars, factors)):
                ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                       f"{factor.description[:40]}...",
                       va='center', fontsize=10, color=self.colors['text'])
        
        # 축 설정
        ax.set_xlim(-1, 1)
        ax.set_xlabel('영향도', color=self.colors['text'])
        ax.tick_params(colors=self.colors['text'])
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        
        for spine in ax.spines.values():
            spine.set_color(self.colors['grid'])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight',
                       facecolor=self.colors['background'])
            
        plt.show()
        return save_path or "chart_displayed"

def demo_enhanced_charts():
    """향상된 차트 데모"""
    print("📊 향상된 차트 시각화 데모")
    print("=" * 50)
    
    chart_gen = EnhancedChartGenerator()
    
    # 샘플 데이터 생성
    np.random.seed(42)
    base_price = 45000
    price_data = pd.Series([
        base_price + np.cumsum(np.random.normal(0, 200, 48))[i] + 1000 * np.sin(i/10)
        for i in range(48)
    ])
    
    current_price = price_data.iloc[-1]
    price_24h_ago = price_data.iloc[0]
    
    print(f"샘플 데이터: {price_24h_ago:.0f} → {current_price:.0f}")
    print(f"변동률: {((current_price - price_24h_ago) / price_24h_ago * 100):+.2f}%")
    
    # 차트 생성
    chart_path = chart_gen.create_price_analysis_chart(
        coin_id="bitcoin",
        price_data=price_data,
        current_price=current_price,
        price_24h_ago=price_24h_ago,
        save_path="sample_price_analysis.png"
    )
    
    print(f"✅ 차트 생성 완료: {chart_path}")

if __name__ == "__main__":
    demo_enhanced_charts()