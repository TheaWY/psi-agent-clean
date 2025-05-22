import pandas as pd
from utils.gpt_wrapper import ask_gpt


def describe_excel_structure(filepath: str):
    xl = pd.ExcelFile(filepath)
    summaries = []

    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        columns = df.columns.tolist()
        num_rows = len(df)

        summaries.append({


            
            "sheet": sheet,
            "columns": columns,
            "num_rows": num_rows
        })

    return summaries

def explain_excel_semantics(filepath: str) -> dict:
    try:
        df = pd.read_excel(filepath, sheet_name=0)
        columns = df.columns.tolist()
        prompt = f"""
다음은 사용자가 업로드한 Excel 문서의 열 구조입니다:

열 목록: {columns}

이 문서는 PSI 관련 문서일 가능성이 높습니다. Sales Forecast, SP, Max SR, BOH, Plan Shortage 등의 항목이 포함되어 있는지 확인한 후, 이 문서가 어떤 용도로 사용되는지 (예: Final PSI, Delay Alloc 등) 간단히 요약해주세요.

또한 중요한 열이 있다면 함께 알려주세요.
"""

        raw = ask_gpt(prompt).strip()

        # GPT 응답이 불확실하거나 거절한 경우도 cover
        if any(kw in raw.lower() for kw in ["판단할 수", "어렵습니다", "알 수 없습니다"]):
            return {
                "status": "fallback",
                "reason": raw,
                "summary": (
                    "이 문서는 Sales PSI 문서로 추정됩니다.\n\n"
                    "- Category별로 Forecast, SP, BOH 등의 값이 주차별로 구성되어 있으며\n"
                    "- Sales Allocation과 Max SR도 함께 포함된 전형적인 PSI 구조입니다.\n\n"
                    "💡 Main SP 및 Max SR 차이를 분석하거나, 재고 부족을 추적하는 데 활용됩니다."
                )
            }

        return {
            "status": "success",
            "summary": raw
        }

    except Exception as e:
        return {
            "status": "error",
            "reason": str(e),
            "summary": "문서 내용을 분석하는 중 오류가 발생했습니다."
        }
