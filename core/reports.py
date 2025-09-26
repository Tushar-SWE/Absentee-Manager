# core/reports.py

import os
import pandas as pd
from datetime import datetime
from .utils import is_valid_date, highlight_absent_cells, get_consec_count_excl_sundays

def generate_absent_reports(df, current_date, id_column, department, base_output_dir="data/absentee_reports"):
    """
    Generate absentee reports for a department and save them locally only.
    """
    reports = {3: [], 6: [], 10: [], "new_absent": []}
    recorded_ids = set()

    output_dir = os.path.join(base_output_dir, department)
    os.makedirs(output_dir, exist_ok=True)

    for _, row in df.iterrows():
        ticket_no = str(row.get(id_column, '')).strip()
        status_today = str(row.get(current_date, '')).strip().upper()

        if not ticket_no or status_today != 'A' or ticket_no in recorded_ids:
            continue

        total_consec, dates = get_consec_count_excl_sundays(row, df, current_date, 20)

        if total_consec in [3, 6, 10]:
            reports[total_consec].append((row, dates))
            recorded_ids.add(ticket_no)
        else:
            valid_dates = [col for col in df.columns if is_valid_date(col)]
            if current_date not in valid_dates:
                continue

            idx = valid_dates.index(current_date)
            for i in range(idx - 1, -1, -1):
                prev_status = str(row.get(valid_dates[i], '')).strip().upper()
                if prev_status == 'SL':
                    continue
                elif prev_status in ['P', 'PL']:
                    reports["new_absent"].append(row)
                    break
                else:
                    break

    saved_files = []

    # Save reports locally
    for count in [3, 6, 10]:
        if reports[count]:
            rows, highlight_sets = zip(*reports[count])
            report_df = pd.DataFrame(rows)
            report_df["Action"] = f"Sent SMS for {count} days leave"
            filename = f"{count}_Consecutive_Absentees_{current_date}.xlsx"
            local_path = os.path.join(output_dir, filename)
            
            styled = report_df.style.apply(
                lambda row: highlight_absent_cells(row, highlight_sets[report_df.index.get_loc(row.name)]),
                axis=1
            )
            styled.to_excel(local_path, index=False, engine='openpyxl')

            saved_files.append(local_path)
            print(f"📄 Report saved locally: {local_path}")

    if reports["new_absent"]:
        report_df = pd.DataFrame(reports["new_absent"])
        report_df["Action"] = "Call and remark"
        filename = f"New_Absentees_{current_date}.xlsx"
        local_path = os.path.join(output_dir, filename)

        styled = report_df.style.apply(lambda row: highlight_absent_cells(row, [current_date]), axis=1)
        styled.to_excel(local_path, index=False, engine='openpyxl')

        saved_files.append(local_path)
        print(f"📄 Report saved locally: {local_path}")

    if not saved_files:
        print("✅ No absentee reports generated (no qualifying absentees found).")

    return saved_files
