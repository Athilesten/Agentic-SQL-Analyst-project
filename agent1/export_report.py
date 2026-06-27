"""
export_report.py
Exports analysis session into a text report.
"""

import os
from datetime import datetime


def export_session(question, sql, columns, result, insight, chart_path=None):

    os.makedirs("exports", exist_ok=True)

    filename = datetime.now().strftime("exports/session_%Y%m%d_%H%M%S.txt")

    with open(filename, "w", encoding="utf-8") as file:

        file.write("AGENTIC SQL ANALYSIS REPORT\n")
        file.write("=" * 50 + "\n\n")

        file.write(f"Question:\n{question}\n\n")

        file.write("Generated SQL:\n")
        file.write(sql + "\n\n")

        file.write("Columns:\n")
        file.write(str(columns) + "\n\n")

        file.write("Result:\n")
        for row in result[:20]:
            file.write(str(row) + "\n")

        file.write("\nInsight:\n")
        file.write(insight + "\n\n")

        if chart_path:
            file.write(f"Chart Path:\n{chart_path}\n")

    return filename