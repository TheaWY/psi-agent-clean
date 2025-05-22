# utils/excel_rule_engine.py

import pandas as pd
import os

# static 파일 경로
STATIC_DIR = "data/static_files"
BOD_FILE    = os.path.join(STATIC_DIR, "item_bod.xlsx")
SS_FILE     = os.path.join(STATIC_DIR, "safety_stock.xlsx")
CTRL_FILE   = os.path.join(STATIC_DIR, "control_panel.xlsx")
MASTER_FILE = os.path.join(STATIC_DIR, "master_control_panel.xlsx")

def analyze_rules(mapping_model_suffix: str, sales_file_path: str) -> dict:
    # 기본 틀
    result = {
        "status": "error",
        "summary": {
            "safety_stock": "안전재고 데이터 없음",
            "bod_start":    "BOD 시작일 데이터 없음",
            "delay_alloc":  "Delay Allocation 데이터 없음"
        },
        "message": ""
    }

    try:
        # 1) Sales 파일 로드 (필터링 용도)
        xls = pd.ExcelFile(sales_file_path)
        sales_df = xls.parse(xls.sheet_names[0])

        # 2) static 파일들 로드
        bod_df    = pd.read_excel(BOD_FILE,    skiprows=1)
        ss_df     = pd.read_excel(SS_FILE)
        ctrl_df   = pd.read_excel(CTRL_FILE)
        master_df = pd.read_excel(MASTER_FILE)

        summary = {}

        # 안전재고
        ss_row = ss_df[ss_df["Mapping Model.Suffix"].astype(str).str.strip() == mapping_model_suffix]
        if not ss_row.empty:
            weeks = int(ss_row.iloc[0]["Safety Stock (W)"])
            summary["safety_stock"] = f"해당 항목의 안전재고는 **{weeks}주**입니다."
        else:
            summary["safety_stock"] = "안전재고 데이터를 찾을 수 없습니다."

        # BOD 시작일
        bod_row = bod_df[bod_df["Mapping Model.Suffix"].astype(str).str.strip() == mapping_model_suffix]
        if not bod_row.empty:
            date = bod_row.iloc[0]["Effective Date"]
            date_str = pd.to_datetime(date).strftime("%Y-%m-%d")
            summary["bod_start"] = f"BOD 기준 시작일은 **{date_str}**입니다."
        else:
            summary["bod_start"] = "Item BOD 데이터를 찾을 수 없습니다."

        # Delay Allocation
        ctrl_row = ctrl_df[ctrl_df["Mapping Model.Suffix"].astype(str).str.strip() == mapping_model_suffix]
        if not ctrl_row.empty:
            site = ctrl_row.iloc[0]["Site"]
            master_row = master_df[master_df["Site"].astype(str).str.strip() == site]
            if not master_row.empty and "Delayed Allocation" in master_row.columns:
                flag = str(master_row.iloc[0]["Delayed Allocation"]).strip().lower()
                if flag in ("on","yes","true"):
                    summary["delay_alloc"] = f"해당 Site (**{site}**)는 `Delay Allocation`이 **On**으로 설정되어 있습니다."
                else:
                    summary["delay_alloc"] = f"해당 Site (**{site}**)는 `Delay Allocation`이 꺼져 있습니다."
            else:
                summary["delay_alloc"] = "Master Control Panel에서 Delay Allocation 설정을 찾을 수 없습니다."
        else:
            summary["delay_alloc"] = "Control Panel에서 해당 모델을 찾을 수 없습니다."

        result["status"]  = "success"
        result["summary"] = summary

    except Exception as e:
        result["message"] = str(e)

    return result
