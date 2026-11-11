import pandas as pd
import matplotlib.pyplot as plt

def plot_backtest_results(results_csv_path='backtest_results.csv'):
    """
    저장된 백테스트 결과 CSV를 읽어와 시각화 차트를 생성하고 저장합니다.
    """
    df = pd.read_csv(results_csv_path, index_col=0, parse_dates=True)
    
    plt.figure(figsize=(10, 5))
    plt.plot(df['KOSPI_Buy_and_Hold'], label='KOSPI Buy & Hold', color='gray', linestyle='--')
    
    # 컬럼명에 따라 동적으로 플롯
    strategy_col = 'Macro_Quant_Strategy' if 'Macro_Quant_Strategy' in df.columns else 'Quant_Strategy_Cum'
    plt.plot(df[strategy_col], label='Macro Quant Strategy (혜안)', color='royalblue', linewidth=2)
    
    plt.title('Macro Quant Strategy vs KOSPI Benchmark', fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=11)
    plt.ylabel('Cumulative Return', fontsize=11)
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    
    output_filename = 'strategy_performance.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"시각화 차트 저장 완료: {output_filename}")
    plt.close()

if __name__ == "__main__":
    plot_backtest_results()
