import pandas as pd
import plotly.express as px

def analyze_trend(row: dict):
    """
    선택된 row의 주차별 값을 분석하여 평균, 주별 그래프, 월별 증감률 표를 반환합니다.
    """
    # 숫자형 값 필터링
    items = [(k, v) for k, v in row.items() if isinstance(v, (int, float))]
    # 주차 순서 정렬 (키에 포함된 숫자를 기준으로)
    def key_num(key):
        nums = ''.join(filter(str.isdigit, key))
        return int(nums) if nums.isdigit() else float('inf')
    items.sort(key=lambda x: key_num(x[0]))
    weeks, values = zip(*items) if items else ([], [])
    series = pd.Series(values, index=weeks)

    # 평균 계산
    avg = series.mean()

    # 주차별 추이 그래프 생성
    fig = px.line(
        x=series.index,
        y=series.values,
        title="주차별 값 추이",
        labels={"x": "주차", "y": "값"}
    )

    # 월별 증감률 계산 (4주 단위 그룹)
    monthly_changes = {}
    n = len(series)
    for i in range(0, n, 4):
        month_label = f"Month{(i // 4) + 1}"
        chunk = series.iloc[i:i+4]
        if len(chunk) >= 2:
            start, end = chunk.iloc[0], chunk.iloc[-1]
            pct = ((end - start) / start * 100) if start != 0 else 0
        else:
            pct = 0
        monthly_changes[month_label] = round(pct, 2)
    monthly_table = pd.DataFrame.from_dict(
        monthly_changes, orient='index', columns=['pct_change(%)']
    )

    return {
        'average': avg,
        'fig': fig,
        'monthly_pct_table': monthly_table
    }
