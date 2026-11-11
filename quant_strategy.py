import pandas as pd
import numpy as np

class MacroQuantStrategy:
    def __init__(self, momentum_lookback=252, macro_lookback=63):
        self.lookback = momentum_lookback
        # 시장의 최근 구조적 변화(Regime Change)를 빠르게 포착하기 위해 매크로 관찰 기간을 3개월(63일)로 설정
        self.macro_lookback = macro_lookback 
        
    def calculate_risk_signals(self, df):
        """
        1. 기간 프리미엄 급등 압력 (3개월간 10년물 국채 금리 상승폭)
        2. 신용 스프레드(Credit Spread) 확대 위험 감지
        """
        # 금리 발작 민감도 상향: 3개월간 금리가 0.1%p 이상 상승하면 기간 프리미엄 확대로 간주
        tp_pressure = df['US10Y'].diff(periods=self.macro_lookback)
        
        # 회사채(LQD)가 장기국채(TLT) 대비 상대 모멘텀이 꺾일 때 크라우딩 아웃 위험으로 간주
        if 'CREDIT_CORP' in df.columns and 'US_BOND' in df.columns:
            credit_health = (df['CREDIT_CORP'] / df['US_BOND']).pct_change(periods=self.macro_lookback)
        else:
            credit_health = pd.Series(1, index=df.index)
            
        return tp_pressure, credit_health

    def generate_comprehensive_guidelines(self, df):
        """
        블로그 본문 5번 항목 완벽 동기화:
        - 듀레이션 관리: 주식/장기채 동반 하락(덫) 회피를 위해 초단기물(Short-duration) 비중 극대화
        """
        momentum = df.pct_change(periods=self.lookback)
        tp_pressure, credit_health = self.calculate_risk_signals(df)
        
        # 포트폴리오 비중: 주식 바벨(KOSPI), 성장주(SP500), 초단기물(SHORT_DURATION), 장기채(US_LONG_BOND)
        signals = pd.DataFrame(index=df.index, columns=['KOSPI_BARBELL', 'SP500_GROWTH', 'SHORT_DURATION', 'US_LONG_BOND'])
        
        for i in range(len(df)):
            if i < self.lookback:
                # 초기 데이터 확보 기간은 동일 비중 처리
                signals.iloc[i] = [0.25, 0.25, 0.25, 0.25]
                continue
                
            kospi_m = momentum['KOSPI'].iloc[i]
            sp500_m = momentum['SP500'].iloc[i]
            
            # 위험 시그널 포착 (민감도 조정 반영)
            tp_up = tp_pressure.iloc[i] > 0.1        # 기간 프리미엄 발작 (금리 상승)
            credit_risk = credit_health.iloc[i] < 0  # 신용 스프레드 확대 (크라우딩 아웃)
            
            if tp_up or credit_risk:
                # [논리 완벽 반영] 밸류에이션 충격 및 신용 경색 국면:
                # 장기채 비중을 0%로 비우고, 고ROE 주식(KOSPI Barbell) 40%와 초단기물(SHORT_DURATION) 60%로 바벨 전략 구축
                signals.iloc[i] = [0.4, 0.0, 0.6, 0.0]
            elif kospi_m > 0 and sp500_m > 0:
                # 정상 장세: 주식 중심 Long 및 보험용 장기채 헷지
                signals.iloc[i] = [0.4, 0.4, 0.0, 0.2]
            else:
                # 단순 경기 둔화 (전통적 하락장): 전통 안전자산(미국 장기채)으로 방어
                signals.iloc[i] = [0.0, 0.0, 0.2, 0.8]
                
        return signals.astype(float)
