"""
CoinCompass - 스마트 암호화폐 투자 나침반

실시간 시장 분석, 기술적 지표, 센티먼트 분석을 통한
종합적인 암호화폐 투자 의사결정 지원 플랫폼
"""

__version__ = "1.0.0"
__author__ = "gum798"
__email__ = "gum798@users.noreply.github.com"

from .core.data_manager import DataManager
from .api.multi_provider import MultiAPIProvider
from .analysis.technical import TechnicalAnalyzer
from .analysis.market_analyzer import MarketAnalyzer
from .analysis.onchain import OnChainAnalyzer, SentimentAnalyzer
from .analysis.macro import MacroeconomicAnalyzer
from .analysis.price_driver import PriceDriverAnalyzer
from .analysis.backtesting import PriceDriverValidator
from .monitoring.real_time import RealTimeMonitor
from .visualization.enhanced_charts import EnhancedChartGenerator
from .reporting.validation_report import ValidationReportGenerator

__all__ = [
    "DataManager",
    "MultiAPIProvider", 
    "TechnicalAnalyzer",
    "MarketAnalyzer",
    "OnChainAnalyzer",
    "SentimentAnalyzer", 
    "MacroeconomicAnalyzer",
    "PriceDriverAnalyzer",
    "PriceDriverValidator",
    "RealTimeMonitor",
    "EnhancedChartGenerator",
    "ValidationReportGenerator"
]