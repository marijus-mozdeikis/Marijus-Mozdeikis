import pandas as pd
import os

def export_peak_results(filename, results, output_file="resonance_properties.xlsx", sheet_name=None, start_row=0):
    """Export peak analysis results to an Excel file."""

    if sheet_name is None:
        sheet_name = os.path.splitext(filename)[0]  # filename without extension

    # Convert results to DataFrame
    df = pd.DataFrame(results)

    # Ensure 'file' column exists
    df["file"] = filename

    # Check if file exists
    file_exists = os.path.exists(output_file)

    # Write to Excel
    with pd.ExcelWriter(output_file, mode="a" if file_exists else "w", engine="openpyxl") as writer:
        # If file exists, remove sheet first if present
        if file_exists and sheet_name in writer.book.sheetnames:
            std = writer.book[sheet_name]
            writer.book.remove(std)
        df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row)

    print(f"Results exported to {output_file}, sheet: {sheet_name}")
