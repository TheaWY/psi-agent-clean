# agents/trend_analysis_agent.py

import pandas as pd
import plotly.express as px

def scenario_trend_analysis(selected_row: dict):
    """
    주차별 트렌드 분석 시나리오
    - selected_row: AgGrid 등에서 받아온 dict 형태의 한 행
    """
    df = pd.DataFrame([selected_row])
    # 숫자형 컬럼만 추출
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        return "❌ 선택한 행에 숫자형 데이터가 없습니다.", None

    series = numeric.iloc[0]

    # 1) 평균
    mean_val = series.mean()

    # 2) 주차별 증감(diff)
    diff = series.diff().fillna(0)

    # 3) 증감률(%)
    pct = (series.pct_change().fillna(0) * 100).round(2)

    # 4) 차트 생성
    fig = px.line(
        x=series.index.astype(str),
        y=series.values,
        title="주차별 값 추이",
        labels={"x": "주차", "y": "값"}
    )

    # 5) 텍스트 리포트
    report = f"📊 **트렌드 분석 결과**\n\n"
    report += f"- 평균 값: **{mean_val:.2f}**\n\n"
    report += "**주차별 증감 (diff)**\n"
    report += diff.to_frame("diff").to_markdown() + "\n\n"
    report += "**주차별 증감률 (%)**\n"
    report += pct.to_frame("pct_change(%)").to_markdown()

    return report, fig
