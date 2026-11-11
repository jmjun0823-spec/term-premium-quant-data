import numpy as np
import pandas as pd

def calculate_performance_metrics(portfolio_returns):
    days = len(portfolio_returns)
    if days == 0:
        return pd.Series({"CAGR (%)": 0, "Volatility (%)": 0, "Sharpe Ratio": 0, "MDD (%)": 0})
        
    cagr = (portfolio_returns.iloc[-1] ** (252 / days)) - 1
    volatility = portfolio_returns.pct_change().std() * np.sqrt(252)
    risk_free_rate = 0.03
    sharpe_ratio = (cagr - risk_free_rate) / volatility if volatility != 0 else 0
    
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
