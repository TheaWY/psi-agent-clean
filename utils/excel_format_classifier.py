# utils/excel_format_classifier.py

import pandas as pd

# 포맷 정의
FORMAT_PROFILES = {
    "sales_psi": {
        "title": "Sales PSI Sheet",
        "sheet_name_keywords": ["psi", "sales"],
        "required_columns": ["Mapping Model.Suffix", "Category"]
    },
    "item_bod": {
        "title": "Item BOD Sheet",
        "sheet_name_keywords": ["bod"],
        "required_columns": ["Mapping Model.Suffix", "BOD Start Date", "Effective Date"]
    },
    "control_panel": {
        "title": "Control Panel Sheet",
        "sheet_name_keywords": ["control", "panel"],
        "required_columns": ["Site", "Delay Allocation", "Frozen Constraint"]
    },
    "safety_stock": {
        "title": "Safety Stock Sheet",
        "sheet_name_keywords": ["safety", "stock"],
        "required_columns": ["Mapping Model.Suffix", "Safety Stock"]
    }
}

def classify_excel_format(file_path: str) -> dict:
    """
    엑셀 파일의 시트명과 헤더(1~2행 병합) 기준으로 포맷을 분류합니다.
    """
    try:
        # 1) 첫 두 행을 병합해서 컬럼명 리스트 추출
        df0 = pd.read_excel(file_path, header=None)
        header1 = df0.iloc[0].fillna("").astype(str).tolist()
        header2 = df0.iloc[1].fillna("").astype(str).tolist()
        if len(header1) == len(header2):
            columns = [
                (h1 + " " + h2).strip()
                for h1, h2 in zip(header1, header2)
                if h1 or h2
            ]
        else:
            # 병합 헤더가 아닐 경우 일반 컬럼 사용
            df = pd.read_excel(file_path)
            columns = df.columns.astype(str).tolist()

        # 2) 시트명도 읽어둡니다.
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names

        # 3) 포맷별 점수 계산
        best = {
            "format_id": "unknown",
            "title": "Unknown Format",
            "matched_columns": [],
            "confidence": 0.0
        }
        best_score = -1

        for fmt_id, profile in FORMAT_PROFILES.items():
            score = 0
            matched = set()

            # (A) 시트명 키워드 매칭
            for kw in profile["sheet_name_keywords"]:
                if any(kw.lower() in sn.lower() for sn in sheet_names):
                    score += 2

            # (B) 필수 컬럼 키워드 매칭
            for req in profile["required_columns"]:
                for col in columns:
                    if req.lower() in col.lower():
                        matched.add(col)
                        score += 1

            # confidence = score / (len(required)*1 + len(sheet_kw)*2)
            max_possible = len(profile["sheet_name_keywords"]) * 2 + len(profile["required_columns"])
            conf = min(score / max_possible, 1.0)

            if score > best_score:
                best_score = score
                best = {
                    "format_id": fmt_id,
                    "title": profile["title"],
                    "matched_columns": list(matched),
                    "confidence": conf
                }

        return best

    except Exception as e:
        return {
            "format_id": "error",
            "title": "Error",
            "matched_columns": [],
            "confidence": 0.0,
            "error": str(e)
        }
