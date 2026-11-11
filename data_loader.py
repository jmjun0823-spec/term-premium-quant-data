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
                # yfinance 최신 버전 다중 인덱스 반환 대비 처리
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
        
    # Series 딕셔너리를 안전하게 DataFrame으로 병합
    df_merged = pd.DataFrame(data).dropna()
    
    # US10Y 스케일 보정 (TNX는 10배 값으로 수집되므로 % 단위로 변환)
    if 'US10Y' in df_merged.columns:
        df_merged['US10Y'] = df_merged['US10Y'] / 10.0
        
    return df_merged

def fetch_domestic_market_details(start_date='20100101', end_date=None):
    """
    pykrx를 활용하여 국내 KOSPI 시장의 거래대금 및 시가총액 등 심층 데이터를 추가 추출합니다.
    """
    if end_date is None:
        end_date = datetime.today().strftime('%Y%m%d')
    kospi_ohlcv = stock.get_index_ohlcv_by_date(start_date, end_date, "1001")
    return kospi_ohlcv[['종가', '거래대금', '시가총액']].rename(
        columns={'종가': 'KOSPI_Close', '거래대금': 'KOSPI_Volume_Amt', '시가총액': 'KOSPI_Market_Cap'}
    )
