# agents/psi_scenario_agent.py

import pandas as pd
from utils.excel_rule_engine import analyze_rules
from utils.gpt_wrapper import stream_gpt_response

# 업로드된 Excel 파일 경로 (app.py 와 동일)
EXCEL_PATH = "data/uploaded_excels/latest.xlsx"

def scenario_max_sr_vs_main_sp(suffix: str):
    rules = analyze_rules(suffix, EXCEL_PATH).get("summary", {})

    safety_txt = rules.get("safety_stock", "안전재고 정보 없음")
    bod_txt    = rules.get("bod_start",     "BOD 시작일 정보 없음")

    prompt = f"""
🔎 [시나리오] Main SP vs Max SR 설명

📌 모델 키: **{suffix}**

1️⃣ 안전재고: {safety_txt}
2️⃣ BOD 시작일: {bod_txt}

위 정보를 바탕으로 Main SP와 Max SR 수립 주차 차이를 설명해주세요.
"""
    return stream_gpt_response(prompt)

def scenario_bod_start_reason(suffix: str):
    rules = analyze_rules(suffix, EXCEL_PATH).get("summary", {})
    bod = rules.get("bod_start")
    if bod:
        return (
            f"✅ 해당 모델의 BOD Start Date는 **{bod}** 입니다.\n\n"
            "GPLM 시스템의 R&D PMS 메뉴에 등록된 개발일정이 GSCP Item BOD 페이지에 I/F되어 반영됩니다."
        )
    return "❌ BOD Start Date 정보를 찾을 수 없습니다."

def scenario_delay_allocation(suffix: str):
    rules = analyze_rules(suffix, EXCEL_PATH).get("summary", {})
    delay = rules.get("delay_alloc")
    if delay:
        return f"✅ {delay}"
    return "❌ Delay Allocation 설정 정보를 찾을 수 없습니다."

def scenario_plan_analysis(suffix: str):
    # 플레이스홀더
    return "🔧 계획 분석 기능은 곧 추가될 예정입니다."
