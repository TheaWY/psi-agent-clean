# agents/trend_analysis_agent.py
import pandas as pd
import plotly.express as px

def scenario_trend_analysis(selected_row: dict):
    """
    주차별 트렌드 분석 시나리오
    - selected_row: AgGrid 에서 넘어온 dict
    """
    def _gen():
        # 1) dict → DataFrame → 숫자만
        df = pd.DataFrame([selected_row])
        numeric = df.select_dtypes(include="number")
        if numeric.empty:
            yield "❌ 선택한 행에 숫자형 데이터가 없습니다."
            return

        series = numeric.iloc[0]

        # 2) 평균
        mean_val = series.mean()

        # 3) 주차별 증감(diff)
        diff = series.diff().fillna(0)

        # 4) 증감률(%)
        pct = series.pct_change().fillna(0) * 100

        # 5) Plotly 차트
        fig = px.line(
            x=series.index.astype(str),
            y=series.values,
            title="주차별 값 추이",
            labels={"x": "주차", "y": "값"}
        )

        # 6) 텍스트 리포트
        report = f"📊 **트렌드 분석 결과**\n\n"
        report += f"- 평균 값: **{mean_val:.2f}**\n\n"
        report += "**주차별 증감 (diff)**\n"
        report += diff.to_frame("diff").to_markdown() + "\n\n"
        report += "**주차별 증감률 (%)**\n"
        report += pct.to_frame("pct_change(%)").to_markdown()

        yield report
        yield fig

    # 제너레이터 팩토리 반환
    return _gen
