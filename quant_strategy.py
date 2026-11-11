import pandas as pd
import numpy as np

class MacroQuantStrategy:
    def __init__(self, momentum_lookback=252):
        self.lookback = momentum_lookback
        
    def calculate_term_premium_signal(self, df):
        """
        1. 기간 프리미엄(Term Premium) 및 10년 국채 금리 상승 압력 정량화
        """
        tp_pressure = df['US10Y'].diff(periods=126) # 반기 기준 금리 급등 압력
        return tp_pressure

    def generate_comprehensive_guidelines(self, df):
        """
        블로그 본문의 5가지 핵심 가이드라인(Top-down, Long/Short, 바벨 전략, 듀레이션 관리)을 완벽히 수식화
        """
        momentum = df.pct_change(periods=self.lookback)
        tp_pressure = self.calculate_term_premium_signal(df)
        
        signals = pd.DataFrame(index=df.index, columns=['KOSPI_BARBELL', 'SP500_GROWTH', 'US_LONG_BOND', 'CASH_DEFENSE'])
        
        for i in range(len(df)):
            if i < self.lookback:
                signals.iloc[i] = [0.25, 0.25, 0.25, 0.25]
                continue
                
            kospi_m = momentum['KOSPI'].iloc[i]
            sp500_m = momentum['SP500'].iloc[i]
            tp_up = tp_pressure.iloc[i] > 0.5 # 기간 프리미엄 급등 국면 (금리 0.5% 이상 급등)
            
            if tp_up and sp500_m < 0:
                # 밸류에이션 충격 (멀티플 콘트랙션) 및 크레딧 리스크 확대 국면 -> 바벨 전략 (고ROE 퀄리티 주식 + 단기채/현금 대피)
                signals.iloc[i] = [0.4, 0.0, 0.2, 0.4]
            elif kospi_m > 0 and sp500_m > 0:
                # 정상 장세: 주식 중심 Long 및 듀레이션 관리
                signals.iloc[i] = [0.4, 0.4, 0.2, 0.0]
            else:
                # Risk-Off 방어 국면: 미국 장기채 및 안전자산 비중 확대
                signals.iloc[i] = [0.0, 0.0, 0.6, 0.4]
                
        return signals.astype(float)
