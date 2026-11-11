import numpy as np
import pandas as pd

def calculate_performance_metrics(portfolio_returns):
    """
    포트폴리오 일간 수익률을 바탕으로 주요 투자 성과 지표를 산출합니다.
    """
    days = len(portfolio_returns)
    if days == 0:
        return pd.Series({"CAGR (%)": 0, "Volatility (%)": 0, "Sharpe Ratio": 0, "MDD (%)": 0})
        
    cagr = (portfolio_returns.iloc[-1] ** (252 / days)) - 1
    volatility = portfolio_returns.pct_change().std() * np.sqrt(252)
    
    # 무위험 수익률 3% 가정
    risk_free_rate = 0.03
    sharpe_ratio = (cagr - risk_free_rate) / volatility if volatility != 0 else 0
    
    # 최대 낙폭 (MDD) 계산
    cum_returns = (1 + portfolio_returns.pct_change()).cumprod()
    peak = cum_returns.cummax()
    drawdown = (cum_returns - peak) / peak
    mdd = drawdown.min()
    
    metrics = {
        "CAGR (%)": round(cagr * 100, 2),
        "Volatility (%)": round(volatility * 100, 2),
        "Sharpe Ratio": round(sharpe_ratio, 2),
        "MDD (%)": round(mdd * 100, 2)
    }
    
    return pd.Series(metrics)
