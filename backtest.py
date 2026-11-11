import pandas as pd
import numpy as np
from data_loader import fetch_comprehensive_macro_data, fetch_domestic_market_details
from quant_strategy import MacroQuantStrategy
from utils import calculate_performance_metrics

def run_engine():
    print("=== [혜안 퀀트 분석 시스템] 전체 매크로 및 기간 프리미엄 데이터 로딩 중 ===")
    df_macro = fetch_comprehensive_macro_data(start_date='2010-01-01')
    
    strategy = MacroQuantStrategy()
    signals = strategy.generate_comprehensive_guidelines(df_macro).shift(1).dropna()
    
    # 자산별 수익률 매핑
    asset_returns = pd.DataFrame({
        'KOSPI_BARBELL': df_macro['KOSPI'].pct_change(),
        'SP500_GROWTH': df_macro['SP500'].pct_change(),
        'SHORT_DURATION': 0.0001, # 초단기물(만기 1~3개월 국채 또는 현금성 자산) 일간 대용 수익률
        'US_LONG_BOND': df_macro['US_BOND'].pct_change()
    }).dropna()
    
    aligned_signals, aligned_returns = signals.align(asset_returns, join='inner', axis=0)
    
    portfolio_daily_returns = (aligned_returns * aligned_signals).sum(axis=1)
    portfolio_cumulative = (1 + portfolio_daily_returns).cumprod()
    benchmark_cumulative = (1 + aligned_returns['KOSPI_BARBELL']).cumprod()
    
    metrics = calculate_performance_metrics(portfolio_cumulative)
    print("\n[혜안 매크로 퀀트 전략 성과 분석 검증 결과]")
    print(metrics)
    
    results_df = pd.DataFrame({
        'KOSPI_Buy_and_Hold': benchmark_cumulative,
        'Macro_Quant_Strategy': portfolio_cumulative
    })
    results_df.to_csv('backtest_results.csv')
    
    latest_signal = aligned_signals.iloc[-1]
    
    print("\n==========================================================")
    print(" [혜안 블로그 리서치 보고서 입증: 최신 자산배분 가이드라인 비중]")
    print(f" 기준 일자: {aligned_signals.index[-1].strftime('%Y-%m-%d')}")
    print("==========================================================")
    for asset, weight in latest_signal.items():
        print(f" - {asset}: {weight * 100:.1f}%")
    print("==========================================================")

if __name__ == "__main__":
    run_engine()
