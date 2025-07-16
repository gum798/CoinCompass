"""
모의투자 시뮬레이션 데이터 모델
가상의 자금으로 암호화폐 투자를 연습할 수 있는 기능
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import uuid

class OrderType(Enum):
    """주문 타입"""
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    """주문 상태"""
    PENDING = "PENDING"      # 대기 중
    EXECUTED = "EXECUTED"    # 체결됨
    CANCELLED = "CANCELLED"  # 취소됨
    FAILED = "FAILED"        # 실패

@dataclass
class Order:
    """주문 정보"""
    id: str
    coin_id: str
    order_type: OrderType
    quantity: float
    price: float
    total_amount: float
    status: OrderStatus
    created_at: datetime
    executed_at: Optional[datetime] = None
    user_id: str = "default"
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

@dataclass
class Position:
    """포지션 정보 (보유 코인)"""
    coin_id: str
    quantity: float
    average_price: float
    total_invested: float
    current_price: float = 0.0
    
    @property
    def current_value(self) -> float:
        """현재 가치"""
        return self.quantity * self.current_price
    
    @property
    def profit_loss(self) -> float:
        """손익 (절대값)"""
        return self.current_value - self.total_invested
    
    @property
    def profit_loss_percent(self) -> float:
        """손익률 (퍼센트)"""
        if self.total_invested == 0:
            return 0.0
        return (self.profit_loss / self.total_invested) * 100

@dataclass
class Portfolio:
    """포트폴리오 정보"""
    user_id: str
    cash_balance: float  # 현금 잔고
    positions: Dict[str, Position]  # 코인별 포지션
    total_orders: int = 0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def total_investment(self) -> float:
        """총 투자 금액"""
        return sum(position.total_invested for position in self.positions.values())
    
    @property
    def total_current_value(self) -> float:
        """총 현재 가치"""
        return sum(position.current_value for position in self.positions.values())
    
    @property
    def total_profit_loss(self) -> float:
        """총 손익"""
        return self.total_current_value - self.total_investment
    
    @property
    def total_profit_loss_percent(self) -> float:
        """총 손익률"""
        if self.total_investment == 0:
            return 0.0
        return (self.total_profit_loss / self.total_investment) * 100
    
    @property
    def total_portfolio_value(self) -> float:
        """총 포트폴리오 가치 (현금 + 코인 가치)"""
        return self.cash_balance + self.total_current_value

@dataclass
class TradingSession:
    """거래 세션 정보"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    initial_balance: float = 100000.0  # 초기 자금 10만 달러
    final_balance: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
    
    @property
    def win_rate(self) -> float:
        """승률"""
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100
    
    @property
    def total_return(self) -> float:
        """총 수익률"""
        if self.initial_balance == 0:
            return 0.0
        return ((self.final_balance - self.initial_balance) / self.initial_balance) * 100

@dataclass
class MarketSimulation:
    """시장 시뮬레이션 설정"""
    session_id: str
    use_real_prices: bool = True  # 실제 가격 사용 여부
    price_volatility: float = 1.0  # 가격 변동성 배수
    trading_fees: float = 0.001  # 거래 수수료 (0.1%)
    slippage: float = 0.001  # 슬리피지 (0.1%)
    
    def apply_trading_costs(self, amount: float) -> float:
        """거래 비용 적용"""
        fee = amount * self.trading_fees
        slippage_cost = amount * self.slippage
        return amount - fee - slippage_cost