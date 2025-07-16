"""
거래 엔진
매수/매도 주문을 처리하고 실행하는 시스템
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from .models import Order, OrderType, OrderStatus, TradingSession, MarketSimulation
from .portfolio_manager import PortfolioManager
from ..api.multi_provider import MultiAPIProvider
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TradingEngine:
    """거래 엔진"""
    
    def __init__(self, data_dir: str = "data/simulation"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.portfolio_manager = PortfolioManager(data_dir)
        self.api_provider = MultiAPIProvider()
        
        # 거래 기록 저장
        self.orders: Dict[str, Order] = {}
        self.trading_sessions: Dict[str, TradingSession] = {}
        
        # 시장 시뮬레이션 설정
        self.market_sim = MarketSimulation(
            session_id="default",
            trading_fees=0.001,  # 0.1% 수수료
            slippage=0.0005     # 0.05% 슬리피지
        )
        
        self.load_orders()
        self.load_sessions()
    
    def get_current_price(self, coin_id: str) -> Optional[float]:
        """현재 가격 조회"""
        try:
            price_data = self.api_provider.get_price_data(coin_id)
            return price_data.price if price_data else None
        except Exception as e:
            logger.error(f"가격 조회 오류 {coin_id}: {str(e)}")
            return None
    
    def create_buy_order(self, user_id: str, coin_id: str, quantity: float, price: Optional[float] = None) -> Tuple[bool, str, Optional[Order]]:
        """매수 주문 생성"""
        portfolio = self.portfolio_manager.get_portfolio(user_id)
        if not portfolio:
            return False, "포트폴리오를 찾을 수 없습니다", None
        
        # 현재 가격 조회
        current_price = price if price else self.get_current_price(coin_id)
        if not current_price:
            return False, f"{coin_id} 가격 정보를 가져올 수 없습니다", None
        
        # 주문 금액 계산
        total_cost = quantity * current_price
        
        # 수수료 및 슬리피지 적용
        total_with_fees = total_cost / self.market_sim.apply_trading_costs(1.0)
        
        # 잔고 확인
        if portfolio.cash_balance < total_with_fees:
            return False, f"잔고가 부족합니다. 필요: ${total_with_fees:.2f}, 보유: ${portfolio.cash_balance:.2f}", None
        
        # 주문 생성
        order = Order(
            id="",  # 자동 생성됨
            coin_id=coin_id,
            order_type=OrderType.BUY,
            quantity=quantity,
            price=current_price,
            total_amount=total_with_fees,
            status=OrderStatus.PENDING,
            created_at=datetime.now(),
            user_id=user_id
        )
        
        # 주문 실행
        success, message = self.execute_order(order)
        if success:
            order.status = OrderStatus.EXECUTED
            order.executed_at = datetime.now()
        else:
            order.status = OrderStatus.FAILED
        
        self.orders[order.id] = order
        self.save_order(order)
        
        return success, message, order
    
    def create_sell_order(self, user_id: str, coin_id: str, quantity: float, price: Optional[float] = None) -> Tuple[bool, str, Optional[Order]]:
        """매도 주문 생성"""
        portfolio = self.portfolio_manager.get_portfolio(user_id)
        if not portfolio:
            return False, "포트폴리오를 찾을 수 없습니다", None
        
        # 보유 수량 확인
        if coin_id not in portfolio.positions:
            return False, f"{coin_id}를 보유하고 있지 않습니다", None
        
        position = portfolio.positions[coin_id]
        if position.quantity < quantity:
            return False, f"매도 수량이 보유 수량을 초과합니다. 보유: {position.quantity}, 매도: {quantity}", None
        
        # 현재 가격 조회
        current_price = price if price else self.get_current_price(coin_id)
        if not current_price:
            return False, f"{coin_id} 가격 정보를 가져올 수 없습니다", None
        
        # 주문 금액 계산 (수수료 및 슬리피지 적용)
        gross_amount = quantity * current_price
        net_amount = self.market_sim.apply_trading_costs(gross_amount)
        
        # 주문 생성
        order = Order(
            id="",  # 자동 생성됨
            coin_id=coin_id,
            order_type=OrderType.SELL,
            quantity=quantity,
            price=current_price,
            total_amount=net_amount,
            status=OrderStatus.PENDING,
            created_at=datetime.now(),
            user_id=user_id
        )
        
        # 주문 실행
        success, message = self.execute_order(order)
        if success:
            order.status = OrderStatus.EXECUTED
            order.executed_at = datetime.now()
        else:
            order.status = OrderStatus.FAILED
        
        self.orders[order.id] = order
        self.save_order(order)
        
        return success, message, order
    
    def execute_order(self, order: Order) -> Tuple[bool, str]:
        """주문 실행"""
        try:
            portfolio = self.portfolio_manager.get_portfolio(order.user_id)
            if not portfolio:
                return False, "포트폴리오를 찾을 수 없습니다"
            
            if order.order_type == OrderType.BUY:
                # 매수 실행
                if portfolio.cash_balance < order.total_amount:
                    return False, "잔고가 부족합니다"
                
                # 현금 차감
                portfolio.cash_balance -= order.total_amount
                
                # 포지션 추가
                success = self.portfolio_manager.add_position(
                    order.user_id, 
                    order.coin_id, 
                    order.quantity, 
                    order.price
                )
                
                if success:
                    portfolio.total_orders += 1
                    logger.info(f"매수 실행: {order.user_id} - {order.coin_id} {order.quantity} @ ${order.price}")
                    return True, "매수 주문이 체결되었습니다"
                else:
                    # 실패시 현금 복원
                    portfolio.cash_balance += order.total_amount
                    return False, "매수 주문 실행 실패"
            
            elif order.order_type == OrderType.SELL:
                # 매도 실행
                success = self.portfolio_manager.remove_position(
                    order.user_id,
                    order.coin_id,
                    order.quantity,
                    order.price
                )
                
                if success:
                    # 현금 추가
                    portfolio.cash_balance += order.total_amount
                    portfolio.total_orders += 1
                    logger.info(f"매도 실행: {order.user_id} - {order.coin_id} {order.quantity} @ ${order.price}")
                    return True, "매도 주문이 체결되었습니다"
                else:
                    return False, "매도 주문 실행 실패"
            
            return False, "알 수 없는 주문 타입"
            
        except Exception as e:
            logger.error(f"주문 실행 오류: {str(e)}")
            return False, f"주문 실행 중 오류 발생: {str(e)}"
    
    def get_user_orders(self, user_id: str, limit: int = 50) -> List[Order]:
        """사용자 주문 내역 조회"""
        user_orders = [order for order in self.orders.values() if order.user_id == user_id]
        user_orders.sort(key=lambda x: x.created_at, reverse=True)
        return user_orders[:limit]
    
    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """주문 ID로 조회"""
        return self.orders.get(order_id)
    
    def cancel_order(self, order_id: str) -> Tuple[bool, str]:
        """주문 취소"""
        order = self.get_order_by_id(order_id)
        if not order:
            return False, "주문을 찾을 수 없습니다"
        
        if order.status != OrderStatus.PENDING:
            return False, "대기 중인 주문만 취소할 수 있습니다"
        
        order.status = OrderStatus.CANCELLED
        self.save_order(order)
        
        return True, "주문이 취소되었습니다"
    
    def update_portfolio_prices(self, user_id: str):
        """포트폴리오 가격 업데이트"""
        portfolio = self.portfolio_manager.get_portfolio(user_id)
        if not portfolio:
            return
        
        current_prices = {}
        for coin_id in portfolio.positions.keys():
            price = self.get_current_price(coin_id)
            if price:
                current_prices[coin_id] = price
        
        self.portfolio_manager.update_position_prices(user_id, current_prices)
    
    def get_trading_summary(self, user_id: str) -> Dict:
        """거래 요약 정보"""
        orders = self.get_user_orders(user_id)
        portfolio = self.portfolio_manager.get_portfolio_summary(user_id)
        
        executed_orders = [o for o in orders if o.status == OrderStatus.EXECUTED]
        buy_orders = [o for o in executed_orders if o.order_type == OrderType.BUY]
        sell_orders = [o for o in executed_orders if o.order_type == OrderType.SELL]
        
        total_bought = sum(o.total_amount for o in buy_orders)
        total_sold = sum(o.total_amount for o in sell_orders)
        
        return {
            'portfolio': portfolio,
            'total_orders': len(orders),
            'executed_orders': len(executed_orders),
            'buy_orders': len(buy_orders),
            'sell_orders': len(sell_orders),
            'total_bought': total_bought,
            'total_sold': total_sold,
            'recent_orders': [self.order_to_dict(o) for o in orders[:10]]
        }
    
    def order_to_dict(self, order: Order) -> Dict:
        """주문 객체를 딕셔너리로 변환"""
        return {
            'id': order.id,
            'coin_id': order.coin_id,
            'order_type': order.order_type.value,
            'quantity': order.quantity,
            'price': order.price,
            'total_amount': order.total_amount,
            'status': order.status.value,
            'created_at': order.created_at.isoformat(),
            'executed_at': order.executed_at.isoformat() if order.executed_at else None
        }
    
    def save_order(self, order: Order):
        """주문 저장"""
        filename = self.data_dir / f"orders_{order.user_id}.json"
        
        # 기존 주문 로드
        orders_data = []
        if filename.exists():
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    orders_data = json.load(f)
            except:
                orders_data = []
        
        # 주문 추가/업데이트
        order_dict = self.order_to_dict(order)
        
        # 기존 주문 업데이트 또는 새 주문 추가
        found = False
        for i, existing_order in enumerate(orders_data):
            if existing_order['id'] == order.id:
                orders_data[i] = order_dict
                found = True
                break
        
        if not found:
            orders_data.append(order_dict)
        
        # 파일 저장
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(orders_data, f, indent=2, ensure_ascii=False)
    
    def load_orders(self):
        """주문 내역 로드"""
        for filename in self.data_dir.glob("orders_*.json"):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    orders_data = json.load(f)
                
                for order_data in orders_data:
                    order = Order(
                        id=order_data['id'],
                        coin_id=order_data['coin_id'],
                        order_type=OrderType(order_data['order_type']),
                        quantity=order_data['quantity'],
                        price=order_data['price'],
                        total_amount=order_data['total_amount'],
                        status=OrderStatus(order_data['status']),
                        created_at=datetime.fromisoformat(order_data['created_at']),
                        executed_at=datetime.fromisoformat(order_data['executed_at']) if order_data.get('executed_at') else None,
                        user_id=filename.stem.replace('orders_', '')
                    )
                    
                    self.orders[order.id] = order
                    
            except Exception as e:
                logger.error(f"주문 로드 오류 {filename}: {str(e)}")
    
    def load_sessions(self):
        """거래 세션 로드"""
        # 추후 구현 예정
        pass