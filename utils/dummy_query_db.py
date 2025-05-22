# utils/dummy_query_db.py

SIMULATED_DATA = [
    {
        "project_code": "PJT001",
        "product": "OLED_PANEL_15.6",
        "max_sr_week": "2025-06W2",
        "main_sp_week": "2025-06W4",
        "final_psi": 1300,
        "sales_alloc": 1450,
        "comment": "수요 급증으로 Alloc이 PSI를 초과함"
    },
    {
        "project_code": "PJT002",
        "product": "BATTERY_PACK_3C",
        "max_sr_week": "2025-07W1",
        "main_sp_week": "2025-07W1",
        "final_psi": 980,
        "sales_alloc": 950,
        "comment": "CAPA 제약에 맞춰 계획 수립됨"
    }
]


def query_simulated_psi_data(user_input: str):
    results = []

    for row in SIMULATED_DATA:
        if row["product"].lower() in user_input.lower() or \
           row["project_code"].lower() in user_input.lower():
            results.append(row)

    return results
