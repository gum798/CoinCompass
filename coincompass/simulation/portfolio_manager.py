"""
포트폴리오 관리 시스템
사용자의 가상 포트폴리오를 관리하고 추적하는 기능
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from .models import Portfolio, Position, Order, OrderType, OrderStatus
from ..utils.logger import get_logger

logger = get_logger(__name__)

class PortfolioManager:
    """포트폴리오 관리자"""
    
    def __init__(self, data_dir: str = "data/simulation"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.portfolios: Dict[str, Portfolio] = {}
        self.load_portfolios()
    
    def create_portfolio(self, user_id: str, initial_balance: float = 100000.0) -> Portfolio:
        """새 포트폴리오 생성"""
        if user_id in self.portfolios:
            logger.warning(f"포트폴리오가 이미 존재합니다: {user_id}")
            return self.portfolios[user_id]
        
        portfolio = Portfolio(
            user_id=user_id,
            cash_balance=initial_balance,
            positions={},
            created_at=datetime.now()
        )
        
        self.portfolios[user_id] = portfolio
        self.save_portfolio(user_id)
        
        logger.info(f"새 포트폴리오 생성: {user_id}, 초기 자금: ${initial_balance:,.2f}")
        return portfolio
    
    def get_portfolio(self, user_id: str) -> Optional[Portfolio]:
        """포트폴리오 조회"""
        return self.portfolios.get(user_id)
    
    def update_position_prices(self, user_id: str, current_prices: Dict[str, float]):
        """포지션의 현재 가격 업데이트"""
        portfolio = self.get_portfolio(user_id)
        if not portfolio:
            return
        
        for coin_id, position in portfolio.positions.items():
            if coin_id in current_prices:
                position.current_price = current_prices[coin_id]
        
        self.save_portfolio(user_id)
    
    def add_position(self, user_id: str, coin_id: str, quantity: float, price: float) -> bool:
        """포지션 추가 (매수)"""
        portfolio = self.get_portfolio(user_id)
        if not portfolio:
            return False
        
        total_cost = quantity * price
        
        if coin_id in portfolio.positions:
            # 기존 포지션 업데이트 (평단가 계산)
            existing = portfolio.positions[coin_id]
            total_quantity = existing.quantity + quantity
            total_invested = existing.total_invested + total_cost
            
            portfolio.positions[coin_id] = Position(
                coin_id=coin_id,
                quantity=total_quantity,
                average_price=total_invested / total_quantity,
                total_invested=total_invested,
                current_price=price
            )
        else:
            # 새 포지션 생성
            portfolio.positions[coin_id] = Position(
                coin_id=coin_id,
                quantity=quantity,
                average_price=price,
                total_invested=total_cost,
                current_price=price
            )
        
        self.save_portfolio(user_id)
        logger.info(f"{user_id}: {coin_id} {quantity} 매수 @ ${price}")
        return True
    
    def remove_position(self, user_id: str, coin_id: str, quantity: float, price: float) -> bool:
        """포지션 제거 (매도)"""
        portfolio = self.get_portfolio(user_id)
        if not portfolio or coin_id not in portfolio.positions:
            return False
        
        position = portfolio.positions[coin_id]
        
        if position.quantity < quantity:
            logger.warning(f"매도 수량이 보유 수량을 초과합니다: {position.quantity} < {quantity}")
            return False
        
        # 매도할 비율만큼 투자금액 감소
        sell_ratio = quantity / position.quantity
        sold_investment = position.total_invested * sell_ratio
        
        position.quantity -= quantity
        position.total_invested -= sold_investment
        
        # 수량이 0이 되면 포지션 삭제
        if position.quantity <= 0:
            del portfolio.positions[coin_id]
        else:
            # 평단가는 변경되지 않음
            pass
        
        self.save_portfolio(user_id)
        logger.info(f"{user_id}: {coin_id} {quantity} 매도 @ ${price}")
        return True
    
    def get_portfolio_summary(self, user_id: str) -> Dict:
        """포트폴리오 요약 정보"""
        portfolio = self.get_portfolio(user_id)
        if not portfolio:
            return {}
        
        positions_data = []
        for coin_id, position in portfolio.positions.items():
            positions_data.append({
                'coin_id': coin_id,
                'quantity': position.quantity,
                'average_price': position.average_price,
                'current_price': position.current_price,
                'total_invested': position.total_invested,
                'current_value': position.current_value,
                'profit_loss': position.profit_loss,
                'profit_loss_percent': position.profit_loss_percent
            })
        
        return {
            'user_id': portfolio.user_id,
            'cash_balance': portfolio.cash_balance,
            'total_investment': portfolio.total_investment,
            'total_current_value': portfolio.total_current_value,
            'total_profit_loss': portfolio.total_profit_loss,
            'total_profit_loss_percent': portfolio.total_profit_loss_percent,
            'total_portfolio_value': portfolio.total_portfolio_value,
            'positions': positions_data,
            'created_at': portfolio.created_at.isoformat() if portfolio.created_at else None
        }
    
    def save_portfolio(self, user_id: str):
        """포트폴리오 저장"""
        portfolio = self.get_portfolio(user_id)
        if not portfolio:
            return
        
        filename = self.data_dir / f"portfolio_{user_id}.json"
        
        # 포트폴리오 데이터를 딕셔너리로 변환
        portfolio_data = {
            'user_id': portfolio.user_id,
            'cash_balance': portfolio.cash_balance,
            'total_orders': portfolio.total_orders,
            'created_at': portfolio.created_at.isoformat() if portfolio.created_at else None,
            'positions': {}
        }
        
        for coin_id, position in portfolio.positions.items():
            portfolio_data['positions'][coin_id] = {
                'coin_id': position.coin_id,
                'quantity': position.quantity,
                'average_price': position.average_price,
                'total_invested': position.total_invested,
                'current_price': position.current_price
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(portfolio_data, f, indent=2, ensure_ascii=False)
    
    def load_portfolios(self):
        """모든 포트폴리오 로드"""
        if not self.data_dir.exists():
            return
        
        for filename in self.data_dir.glob("portfolio_*.json"):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 포지션 데이터 복원
                positions = {}
                for coin_id, pos_data in data.get('positions', {}).items():
                    positions[coin_id] = Position(
                        coin_id=pos_data['coin_id'],
                        quantity=pos_data['quantity'],
                        average_price=pos_data['average_price'],
                        total_invested=pos_data['total_invested'],
                        current_price=pos_data.get('current_price', 0.0)
                    )
                
                # 포트폴리오 복원
                portfolio = Portfolio(
                    user_id=data['user_id'],
                    cash_balance=data['cash_balance'],
                    positions=positions,
                    total_orders=data.get('total_orders', 0),
                    created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
                )
                
                self.portfolios[data['user_id']] = portfolio
                logger.debug(f"포트폴리오 로드됨: {data['user_id']}")
                
            except Exception as e:
                logger.error(f"포트폴리오 로드 오류 {filename}: {str(e)}")
    
    def reset_portfolio(self, user_id: str, initial_balance: float = 100000.0):
        """포트폴리오 리셋"""
        portfolio = Portfolio(
            user_id=user_id,
            cash_balance=initial_balance,
            positions={},
            created_at=datetime.now()
        )
        
        self.portfolios[user_id] = portfolio
        self.save_portfolio(user_id)
        
        logger.info(f"포트폴리오 리셋: {user_id}, 초기 자금: ${initial_balance:,.2f}")
        return portfolio
    
    def get_all_portfolios(self) -> Dict[str, Portfolio]:
        """모든 포트폴리오 조회"""
        return self.portfolios.copy()