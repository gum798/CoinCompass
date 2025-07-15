"""
데이터 포맷팅 유틸리티
"""

def format_price(price: float, currency: str = "USD") -> str:
    """가격 포맷팅"""
    if price is None:
        return "N/A"
    
    if currency == "USD":
        if price >= 1:
            return f"${price:,.2f}"
        else:
            return f"${price:.6f}"
    else:
        return f"{price:,.2f} {currency}"

def format_percentage(percentage: float, decimals: int = 2) -> str:
    """퍼센트 포맷팅"""
    if percentage is None:
        return "N/A"
    
    sign = "+" if percentage > 0 else ""
    return f"{sign}{percentage:.{decimals}f}%"

def format_market_cap(market_cap: float) -> str:
    """시가총액 포맷팅"""
    if market_cap is None:
        return "N/A"
    
    if market_cap >= 1e12:
        return f"${market_cap/1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"${market_cap/1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap/1e6:.2f}M"
    elif market_cap >= 1e3:
        return f"${market_cap/1e3:.2f}K"
    else:
        return f"${market_cap:,.0f}"

def format_volume(volume: float) -> str:
    """거래량 포맷팅"""
    return format_market_cap(volume)

def format_datetime(dt, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """날짜시간 포맷팅"""
    if dt is None:
        return "N/A"
    
    return dt.strftime(format_string)

def truncate_string(text: str, max_length: int = 50) -> str:
    """문자열 자르기"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."