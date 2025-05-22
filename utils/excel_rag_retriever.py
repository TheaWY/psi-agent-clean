import pandas as pd
import os
import difflib

def retrieve_excel_context(user_input: str, excel_dir="data/excel_uploads", max_docs=3):
    """
    사용자 질문과 가장 관련 있는 셀 내용을 포함한 문맥을 추출합니다.
    현재는 간단한 keyword 유사도 기반으로 동작합니다.

    Parameters:
    - user_input: 사용자의 질문
    - excel_dir: Excel 파일이 저장된 디렉토리
    - max_docs: 최대 반환 문서 수

    Returns:
    - List[str]: 유사한 문맥을 가진 셀 내용들
    """

    context_blocks = []

    if not os.path.exists(excel_dir):
        return ["❌ 업로드된 Excel 파일이 없습니다."]

    for file in os.listdir(excel_dir):
        if file.endswith(".xlsx") or file.endswith(".xls"):
            file_path = os.path.join(excel_dir, file)
            try:
                xl = pd.ExcelFile(file_path)
                for sheet_name in xl.sheet_names:
                    df = xl.parse(sheet_name)
                    for i, row in df.iterrows():
                        for col in df.columns:
                            cell = str(row[col])
                            # 간단한 유사도 기준 필터링
                            if difflib.SequenceMatcher(None, user_input.lower(), cell.lower()).ratio() > 0.5:
                                snippet = f"📂 {file} > {sheet_name} [{col}{i+2}]: {cell}"
                                context_blocks.append(snippet)
                                if len(context_blocks) >= max_docs:
                                    return context_blocks
            except Exception as e:
                context_blocks.append(f"⚠️ 파일 {file} 처리 중 오류 발생: {str(e)}")

    if not context_blocks:
        return ["ℹ️ 관련된 내용을 Excel 문서에서 찾을 수 없습니다. 좀 더 구체적으로 입력해 주세요."]

    return context_blocks
