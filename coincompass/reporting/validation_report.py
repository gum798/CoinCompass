"""
검증 보고서 생성 모듈
백테스팅 결과를 시각화하고 상세한 검증 보고서 생성
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

from ..analysis.backtesting import BacktestReport, ValidationResult, PriceDriverValidator
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ValidationReportGenerator:
    """검증 보고서 생성기"""
    
    def __init__(self):
        self.validator = PriceDriverValidator()
        
        # 한글 폰트 설정
        plt.rcParams['font.family'] = ['AppleGothic', 'Malgun Gothic', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 색상 테마
        self.colors = {
            'background': '#1e1e1e',
            'text': '#ffffff',
            'grid': '#404040',
            'correct': '#26a69a',
            'incorrect': '#ef5350',
            'neutral': '#90a4ae',
            'highlight': '#ffeb3b',
            'panel_bg': '#2d2d2d'
        }
    
    def generate_comprehensive_validation_report(self, coin_id: str, days: int = 30,
                                               save_path: Optional[str] = None) -> str:
        """종합 검증 보고서 생성"""
        
        logger.info(f"📊 {coin_id} 종합 검증 보고서 생성 중...")
        
        # 백테스팅 수행
        report = self.validator.validate_price_predictions(coin_id, days)
        
        # 보고서 차트 생성
        fig = plt.figure(figsize=(20, 16))
        fig.patch.set_facecolor(self.colors['background'])
        
        # 그리드 설정 (4x3)
        gs = fig.add_gridspec(4, 3, height_ratios=[1, 1, 1, 1.5], hspace=0.3, wspace=0.3)
        
        # 1. 전체 정확도 요약
        ax_summary = fig.add_subplot(gs[0, :])
        self._plot_accuracy_summary(ax_summary, report)
        
        # 2. 변동 유형별 정확도
        ax_movement = fig.add_subplot(gs[1, 0])
        self._plot_movement_accuracy(ax_movement, report)
        
        # 3. 요인별 효과성
        ax_factors = fig.add_subplot(gs[1, 1])
        self._plot_factor_effectiveness(ax_factors, report)
        
        # 4. 신뢰도 분포
        ax_confidence = fig.add_subplot(gs[1, 2])
        self._plot_confidence_distribution(ax_confidence, report)
        
        # 5. 시간별 정확도 추이
        ax_timeline = fig.add_subplot(gs[2, :])
        self._plot_accuracy_timeline(ax_timeline, report)
        
        # 6. 상세 분석 텍스트
        ax_details = fig.add_subplot(gs[3, :])
        self._plot_detailed_analysis(ax_details, report)
        
        # 전체 제목
        title = f"🧭 CoinCompass 가격 변동 분석 검증 보고서 - {coin_id.upper()}"
        fig.suptitle(title, fontsize=24, color=self.colors['text'], fontweight='bold', y=0.98)
        
        # 저장
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                       facecolor=self.colors['background'], edgecolor='none')
            logger.info(f"💾 검증 보고서 저장: {save_path}")
        
        plt.show()
        
        # 텍스트 보고서도 생성
        text_report = self._generate_text_report(coin_id, report)
        
        if save_path:
            text_path = save_path.replace('.png', '_report.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text_report)
            logger.info(f"📄 텍스트 보고서 저장: {text_path}")
        
        return save_path or "report_displayed"
    
    def _plot_accuracy_summary(self, ax, report: BacktestReport):
        """전체 정확도 요약 차트"""
        ax.set_facecolor(self.colors['background'])
        
        # 정확도 원형 차트
        sizes = [report.correct_predictions, report.total_predictions - report.correct_predictions]
        labels = ['정확한 예측', '부정확한 예측']
        colors = [self.colors['correct'], self.colors['incorrect']]
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                         startangle=90, textprops={'color': self.colors['text']})
        
        # 중앙에 정확도 표시
        ax.text(0, 0, f"{report.accuracy_rate:.1%}", ha='center', va='center',
                fontsize=32, fontweight='bold', color=self.colors['highlight'])
        
        ax.set_title('📊 전체 정확도', color=self.colors['text'], fontsize=16, fontweight='bold')
        
        # 통계 정보 추가
        stats_text = f"총 예측: {report.total_predictions}회\n"
        stats_text += f"정확한 예측: {report.correct_predictions}회\n"
        stats_text += f"검증 기간: {report.period}"
        
        ax.text(1.3, 0, stats_text, transform=ax.transAxes, fontsize=12, 
                color=self.colors['text'], verticalalignment='center',
                bbox=dict(boxstyle='round,pad=0.5', facecolor=self.colors['panel_bg'], alpha=0.8))
    
    def _plot_movement_accuracy(self, ax, report: BacktestReport):
        """변동 유형별 정확도 차트"""
        ax.set_facecolor(self.colors['background'])
        
        movements = list(report.movement_type_accuracy.keys())
        accuracies = list(report.movement_type_accuracy.values())
        
        # 막대 색상 설정
        colors = [self.colors['correct'] if acc >= 0.6 else 
                 self.colors['neutral'] if acc >= 0.4 else 
                 self.colors['incorrect'] for acc in accuracies]
        
        bars = ax.bar(movements, accuracies, color=colors, alpha=0.8)
        
        # 값 표시
        for bar, acc in zip(bars, accuracies):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f'{acc:.1%}', ha='center', va='bottom', 
                   color=self.colors['text'], fontweight='bold')
        
        ax.set_title('📈 변동 유형별 정확도', color=self.colors['text'], fontweight='bold')
        ax.set_ylabel('정확도', color=self.colors['text'])
        ax.set_ylim(0, 1)
        ax.tick_params(colors=self.colors['text'])
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        
        # 축 색상 설정
        for spine in ax.spines.values():
            spine.set_color(self.colors['grid'])
        
        # X축 라벨 회전
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    def _plot_factor_effectiveness(self, ax, report: BacktestReport):
        """요인별 효과성 차트"""
        ax.set_facecolor(self.colors['background'])
        
        if not report.factor_effectiveness:
            ax.text(0.5, 0.5, '요인 데이터 없음', ha='center', va='center',
                   transform=ax.transAxes, color=self.colors['text'])
            return
        
        factors = list(report.factor_effectiveness.keys())
        effectiveness = list(report.factor_effectiveness.values())
        
        # 요인별 색상 매핑
        factor_colors = {
            'technical': '#2196F3',
            'sentiment': '#FF9800', 
            'macro': '#4CAF50',
            'structural': '#9C27B0'
        }
        
        colors = [factor_colors.get(factor, self.colors['neutral']) for factor in factors]
        
        bars = ax.barh(factors, effectiveness, color=colors, alpha=0.8)
        
        # 값 표시
        for bar, eff in zip(bars, effectiveness):
            ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                   f'{eff:.1%}', ha='left', va='center',
                   color=self.colors['text'], fontweight='bold')
        
        ax.set_title('🔍 요인별 효과성', color=self.colors['text'], fontweight='bold')
        ax.set_xlabel('효과성', color=self.colors['text'])
        ax.set_xlim(0, 1)
        ax.tick_params(colors=self.colors['text'])
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        
        for spine in ax.spines.values():
            spine.set_color(self.colors['grid'])
    
    def _plot_confidence_distribution(self, ax, report: BacktestReport):
        """신뢰도 분포 차트"""
        ax.set_facecolor(self.colors['background'])
        
        confidences = [result.confidence for result in report.validation_results]
        
        if not confidences:
            ax.text(0.5, 0.5, '신뢰도 데이터 없음', ha='center', va='center',
                   transform=ax.transAxes, color=self.colors['text'])
            return
        
        # 히스토그램
        n, bins, patches = ax.hist(confidences, bins=10, alpha=0.7, 
                                  color=self.colors['highlight'], edgecolor=self.colors['text'])
        
        # 평균 신뢰도 표시
        mean_confidence = np.mean(confidences)
        ax.axvline(mean_confidence, color=self.colors['correct'], 
                  linestyle='--', linewidth=2, label=f'평균: {mean_confidence:.1%}')
        
        ax.set_title('📊 예측 신뢰도 분포', color=self.colors['text'], fontweight='bold')
        ax.set_xlabel('신뢰도', color=self.colors['text'])
        ax.set_ylabel('빈도', color=self.colors['text'])
        ax.tick_params(colors=self.colors['text'])
        ax.legend(facecolor=self.colors['panel_bg'], edgecolor=self.colors['grid'])
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        
        for spine in ax.spines.values():
            spine.set_color(self.colors['grid'])
    
    def _plot_accuracy_timeline(self, ax, report: BacktestReport):
        """시간별 정확도 추이"""
        ax.set_facecolor(self.colors['background'])
        
        if not report.validation_results:
            ax.text(0.5, 0.5, '시계열 데이터 없음', ha='center', va='center',
                   transform=ax.transAxes, color=self.colors['text'])
            return
        
        # 최근 결과들의 정확도 추이
        recent_results = report.validation_results[-20:]  # 최근 20개
        
        dates = [datetime.strptime(result.date, '%Y-%m-%d %H:%M') for result in recent_results]
        accuracies = [1 if result.accuracy else 0 for result in recent_results]
        
        # 이동평균 계산
        window_size = 5
        moving_avg = pd.Series(accuracies).rolling(window=window_size, center=True).mean()
        
        # 개별 예측 정확도
        colors = [self.colors['correct'] if acc else self.colors['incorrect'] for acc in accuracies]
        ax.scatter(dates, accuracies, c=colors, s=50, alpha=0.7, zorder=3)
        
        # 이동평균 선
        ax.plot(dates, moving_avg, color=self.colors['highlight'], linewidth=2, 
               label=f'{window_size}점 이동평균', zorder=2)
        
        ax.set_title('⏰ 시간별 예측 정확도 추이', color=self.colors['text'], fontweight='bold')
        ax.set_ylabel('정확도 (1=정확, 0=부정확)', color=self.colors['text'])
        ax.set_ylim(-0.1, 1.1)
        ax.tick_params(colors=self.colors['text'])
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        ax.legend(facecolor=self.colors['panel_bg'], edgecolor=self.colors['grid'])
        
        # X축 날짜 포맷
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        for spine in ax.spines.values():
            spine.set_color(self.colors['grid'])
    
    def _plot_detailed_analysis(self, ax, report: BacktestReport):
        """상세 분석 텍스트"""
        ax.set_facecolor(self.colors['background'])
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        
        # 축 숨기기
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # 제목
        ax.text(5, 9.5, '📋 상세 분석 결과', ha='center', va='top',
                fontsize=18, color=self.colors['text'], fontweight='bold')
        
        # 핵심 발견사항
        y_pos = 8.5
        
        # 1. 전체 성능 평가
        performance_grade = self._get_performance_grade(report.accuracy_rate)
        ax.text(0.5, y_pos, f"🎯 전체 성능: {performance_grade}", 
                fontsize=14, color=self.colors['text'], fontweight='bold')
        y_pos -= 0.7
        
        # 2. 최고 성능 변동 유형
        if report.movement_type_accuracy:
            best_movement = max(report.movement_type_accuracy.items(), key=lambda x: x[1])
            ax.text(0.5, y_pos, f"📈 최고 정확도 변동 유형: {best_movement[0]} ({best_movement[1]:.1%})",
                    fontsize=12, color=self.colors['text'])
            y_pos -= 0.5
        
        # 3. 최고 효과 요인
        if report.factor_effectiveness:
            best_factor = max(report.factor_effectiveness.items(), key=lambda x: x[1])
            ax.text(0.5, y_pos, f"🔍 최고 효과 요인: {best_factor[0]} ({best_factor[1]:.1%})",
                    fontsize=12, color=self.colors['text'])
            y_pos -= 0.5
        
        # 4. 개선 권장사항
        recommendations = self._generate_recommendations(report)
        ax.text(0.5, y_pos, "💡 개선 권장사항:", fontsize=14, 
                color=self.colors['highlight'], fontweight='bold')
        y_pos -= 0.5
        
        for i, rec in enumerate(recommendations[:3]):  # 최대 3개
            ax.text(1, y_pos, f"• {rec}", fontsize=11, color=self.colors['text'])
            y_pos -= 0.4
        
        # 5. 신뢰도 평가
        if report.validation_results:
            avg_confidence = np.mean([r.confidence for r in report.validation_results])
            ax.text(0.5, y_pos, f"🎲 평균 예측 신뢰도: {avg_confidence:.1%}",
                    fontsize=12, color=self.colors['text'])
    
    def _get_performance_grade(self, accuracy: float) -> str:
        """성능 등급 반환"""
        if accuracy >= 0.8:
            return "A급 (우수) ⭐⭐⭐"
        elif accuracy >= 0.7:
            return "B급 (양호) ⭐⭐"
        elif accuracy >= 0.6:
            return "C급 (보통) ⭐"
        elif accuracy >= 0.5:
            return "D급 (미흡) ⚠️"
        else:
            return "F급 (부족) ❌"
    
    def _generate_recommendations(self, report: BacktestReport) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        # 전체 정확도 기반
        if report.accuracy_rate < 0.6:
            recommendations.append("전체 정확도가 낮음. 알고리즘 개선 필요")
        
        # 변동 유형별 분석
        if report.movement_type_accuracy:
            worst_movement = min(report.movement_type_accuracy.items(), key=lambda x: x[1])
            if worst_movement[1] < 0.4:
                recommendations.append(f"{worst_movement[0]} 변동 예측 정확도 개선 필요")
        
        # 요인별 분석
        if report.factor_effectiveness:
            weak_factors = [factor for factor, eff in report.factor_effectiveness.items() if eff < 0.5]
            if weak_factors:
                recommendations.append(f"{', '.join(weak_factors)} 요인 분석 강화 필요")
        
        # 신뢰도 분석
        if report.validation_results:
            avg_confidence = np.mean([r.confidence for r in report.validation_results])
            if avg_confidence < 0.6:
                recommendations.append("예측 신뢰도 개선을 위한 데이터 품질 향상 필요")
        
        # 기본 권장사항
        if not recommendations:
            recommendations.append("현재 성능이 양호함. 지속적인 모니터링 권장")
        
        return recommendations
    
    def _generate_text_report(self, coin_id: str, report: BacktestReport) -> str:
        """텍스트 보고서 생성"""
        text_report = f"""
🧭 CoinCompass 가격 변동 분석 검증 보고서
======================================================

📊 기본 정보
• 분석 대상: {coin_id.upper()}
• 검증 기간: {report.period}
• 생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 전체 성능 요약
• 총 예측 횟수: {report.total_predictions}회
• 정확한 예측: {report.correct_predictions}회
• 전체 정확도: {report.accuracy_rate:.1%}
• 성능 등급: {self._get_performance_grade(report.accuracy_rate)}

📊 변동 유형별 정확도
"""
        
        for movement, accuracy in report.movement_type_accuracy.items():
            text_report += f"• {movement}: {accuracy:.1%}\n"
        
        text_report += "\n🔍 요인별 효과성\n"
        for factor, effectiveness in report.factor_effectiveness.items():
            text_report += f"• {factor}: {effectiveness:.1%}\n"
        
        text_report += f"\n💡 개선 권장사항\n"
        recommendations = self._generate_recommendations(report)
        for i, rec in enumerate(recommendations, 1):
            text_report += f"{i}. {rec}\n"
        
        text_report += f"\n📝 종합 평가\n{report.summary}\n"
        
        return text_report

def demo_validation_report():
    """검증 보고서 데모"""
    print("📊 CoinCompass 검증 보고서 생성 데모")
    print("=" * 60)
    
    reporter = ValidationReportGenerator()
    
    try:
        # 비트코인 검증 보고서 생성
        report_path = f"reports/bitcoin_validation_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
        
        print("📊 비트코인 검증 보고서 생성 중...")
        result_path = reporter.generate_comprehensive_validation_report(
            coin_id="bitcoin",
            days=30,
            save_path=report_path
        )
        
        print(f"✅ 검증 보고서 생성 완료: {result_path}")
        
    except Exception as e:
        logger.error(f"검증 보고서 생성 오류: {str(e)}")
        print(f"❌ 보고서 생성 실패: {str(e)}")

if __name__ == "__main__":
    demo_validation_report()