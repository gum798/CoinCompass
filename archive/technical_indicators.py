import pandas as pd
import numpy as np

class TechnicalIndicators:
    """기술적 지표 계산 클래스"""
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """RSI (Relative Strength Index) 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_sma(prices, period=20):
        """단순 이동평균 (Simple Moving Average) 계산"""
        return prices.rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(prices, period=20):
        """지수 이동평균 (Exponential Moving Average) 계산"""
        return prices.ewm(span=period).mean()
    
    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """MACD 계산"""
        ema_fast = TechnicalIndicators.calculate_ema(prices, fast)
        ema_slow = TechnicalIndicators.calculate_ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return pd.DataFrame({
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        })
    
    @staticmethod
    def calculate_bollinger_bands(prices, period=20, std_dev=2):
        """볼린저 밴드 계산"""
        sma = TechnicalIndicators.calculate_sma(prices, period)
        std = prices.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return pd.DataFrame({
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        })

class TradingSignals:
    """매매 신호 생성 클래스"""
    
    @staticmethod
    def rsi_signals(rsi, oversold=30, overbought=70):
        """RSI 기반 매매 신호"""
        signals = pd.Series(index=rsi.index, dtype=str)
        signals[:] = 'HOLD'
        
        signals[rsi < oversold] = 'BUY'
        signals[rsi > overbought] = 'SELL'
        
        return signals
    
    @staticmethod
    def moving_average_crossover(short_ma, long_ma):
        """이동평균 교차 신호"""
        signals = pd.Series(index=short_ma.index, dtype=str)
        signals[:] = 'HOLD'
        
        # 골든 크로스 (단기MA가 장기MA를 상향돌파)
        golden_cross = (short_ma > long_ma) & (short_ma.shift(1) <= long_ma.shift(1))
        signals[golden_cross] = 'BUY'
        
        # 데드 크로스 (단기MA가 장기MA를 하향돌파)
        death_cross = (short_ma < long_ma) & (short_ma.shift(1) >= long_ma.shift(1))
        signals[death_cross] = 'SELL'
        
        return signals

def analyze_coin(prices_df, coin_name="Bitcoin"):
    """코인 기술적 분석 수행"""
    prices = prices_df['price']
    
    # 기술적 지표 계산
    rsi = TechnicalIndicators.calculate_rsi(prices)
    sma_short = TechnicalIndicators.calculate_sma(prices, 5)
    sma_long = TechnicalIndicators.calculate_sma(prices, 20)
    macd_data = TechnicalIndicators.calculate_macd(prices)
    bollinger = TechnicalIndicators.calculate_bollinger_bands(prices)
    
    # 매매 신호 생성
    rsi_signals = TradingSignals.rsi_signals(rsi)
    ma_signals = TradingSignals.moving_average_crossover(sma_short, sma_long)
    
    # 결과 DataFrame 생성
    analysis = pd.DataFrame({
        'price': prices,
        'rsi': rsi,
        'sma_5': sma_short,
        'sma_20': sma_long,
        'macd': macd_data['macd'],
        'macd_signal': macd_data['signal'],
        'bb_upper': bollinger['upper'],
        'bb_middle': bollinger['middle'],
        'bb_lower': bollinger['lower'],
        'rsi_signal': rsi_signals,
        'ma_signal': ma_signals
    })
    
    return analysis

def print_latest_analysis(analysis, coin_name="Bitcoin"):
    """최신 분석 결과 출력"""
    latest = analysis.iloc[-1]
    
    print(f"\n=== {coin_name} 최신 기술적 분석 ===")
    print(f"현재 가격: ${latest['price']:,.2f}")
    print(f"RSI: {latest['rsi']:.2f}")
    print(f"5일 이평: ${latest['sma_5']:,.2f}")
    print(f"20일 이평: ${latest['sma_20']:,.2f}")
    print(f"MACD: {latest['macd']:.2f}")
    print(f"볼린저 상단: ${latest['bb_upper']:,.2f}")
    print(f"볼린저 하단: ${latest['bb_lower']:,.2f}")
    print(f"RSI 신호: {latest['rsi_signal']}")
    print(f"이동평균 신호: {latest['ma_signal']}")
    
    # 종합 판단
    signals = [latest['rsi_signal'], latest['ma_signal']]
    buy_count = signals.count('BUY')
    sell_count = signals.count('SELL')
    
    if buy_count > sell_count:
        recommendation = "매수 신호"
    elif sell_count > buy_count:
        recommendation = "매도 신호"
    else:
        recommendation = "관망"
    
    print(f"종합 판단: {recommendation}")