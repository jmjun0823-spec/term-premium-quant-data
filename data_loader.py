import yfinance as yf
from pykrx import stock
import pandas as pd
from datetime import datetime

def fetch_comprehensive_macro_data(start_date='2010-01-01', end_date=None):
    """
    블로그 본문에 언급된 모든 핵심 매크로 지표를 완벽히 수집합니다.
    """
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
    
    tickers = {
        'US10Y': '^TNX',       # 미국 10년 국채 금리 (기간 프리미엄 프록시)
        'US2Y': '^2YY',        # 미국 2년 국채 금리
        'SP500': '^GSPC',      # S&P 500 (밸류에이션 딜레이 검증)
        'KOSPI': '^KS11',      # KOSPI 지수
        'US_BOND': 'TLT',      # 미국 장기채 (10년 이상)
        'CREDIT_CORP': 'LQD',  # 미국 회사채 (크레딧 스프레드 입증)
        'USD_KRW': 'KRW=X'     # 원/달러 환율
    }
    
    data = {}
    for name, ticker in tickers.items():
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        data[name] = df['Close']
        
    df_merged = pd.DataFrame(data).dropna()
    # US10Y 스케일 보정 (TNX는 10배 값으로 표시되므로 % 단위로 변환)
    if 'US10Y' in df_merged.columns:
        df_merged['US10Y'] = df_merged['US10Y'] / 10.0
    if 'US2Y' in df_merged.columns:
        df_merged['US2Y'] = df_merged['US2Y'] / 10.0
        
    return df_merged

def fetch_domestic_market_details(start_date='20100101', end_date=None):
    if end_date is None:
        end_date = datetime.today().strftime('%Y%m%d')
    kospi_ohlcv = stock.get_index_ohlcv_by_date(start_date, end_date, "1001")
    return kospi_ohlcv[['종가', '거래대금', '시가총액']].rename(
        columns={'종가': 'KOSPI_Close', '거래대금': 'KOSPI_Volume_Amt', '시가총액': 'KOSPI_Market_Cap'}
    )
