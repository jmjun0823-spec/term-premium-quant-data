import yfinance as yf
from pykrx import stock
import pandas as pd
from datetime import datetime

def fetch_comprehensive_macro_data(start_date='2010-01-01', end_date=None):
    """
    블로그 본문에 언급된 모든 핵심 지표를 안전하게 수집합니다.
    (야후 파이낸스 불안정 티커 제외 및 에러 예외 처리 적용)
    """
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
    
    tickers = {
        'US10Y': '^TNX',       # 미국 10년 국채 금리 (기간 프리미엄 프록시)
        'SP500': '^GSPC',      # S&P 500
        'KOSPI': '^KS11',      # KOSPI 지수
        'US_BOND': 'TLT',      # 미국 장기채 (10년 이상)
        'CREDIT_CORP': 'LQD',  # 미국 회사채 (크레딧 스프레드 입증)
        'USD_KRW': 'KRW=X'     # 원/달러 환율
    }
    
    data = {}
    for name, ticker in tickers.items():
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if not df.empty and 'Close' in df.columns:
                close_series = df['Close']
                if isinstance(close_series, pd.DataFrame):
                    close_series = close_series.iloc[:, 0]
                data[name] = close_series.dropna()
            else:
                print(f"[Warning] {ticker} 데이터를 불러오지 못했습니다.")
        except Exception as e:
            print(f"[Error] {ticker} 수집 중 예외 발생: {e}")
            
    if not data:
        raise ValueError("수집된 데이터가 없습니다. (야후 파이낸스 일시적 차단 또는 네트워크 에러)")
        
    df_merged = pd.DataFrame(data).dropna()
    
    if 'US10Y' in df_merged.columns:
        df_merged['US10Y'] = df_merged['US10Y'] / 10.0
        
    return df_merged

def fetch_domestic_market_details(start_date='20100101', end_date=None):
    """
    pykrx를 활용하여 국내 시장 데이터를 추출하되, KRX IP 차단 시 파이프라인 중단을 방지합니다.
    """
    if end_date is None:
        end_date = datetime.today().strftime('%Y%m%d')
        
    try:
        kospi_ohlcv = stock.get_index_ohlcv_by_date(start_date, end_date, "1001")
        if not kospi_ohlcv.empty and '종가' in kospi_ohlcv.columns:
            return kospi_ohlcv[['종가', '거래대금', '시가총액']].rename(
                columns={'종가': 'KOSPI_Close', '거래대금': 'KOSPI_Volume_Amt', '시가총액': 'KOSPI_Market_Cap'}
            )
    except Exception as e:
        print(f"[Warning] KRX IP 차단 등으로 인해 pykrx 국내 데이터 수집을 건너뜁니다: {e}")
        
    # 에러 발생 시 빈 데이터프레임을 반환하여 메인 엔진이 중단되지 않도록 보호
    return pd.DataFrame()
