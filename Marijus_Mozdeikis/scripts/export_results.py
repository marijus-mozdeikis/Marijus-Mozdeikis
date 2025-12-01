import pandas as pd
import os

def export_peak_results(filename, results, output_file="resonance_properties.xlsx", sheet_name="All_Results"):
    """Export peak analysis results to an Excel file.
    Appends new results without overwriting existing data."""
    
    # Always use same sheet name for all files
    sheet_name = "All_Results"
    
    # Convert results to DataFrame
    df_new = pd.DataFrame(results)
    
    # Ensure required columns exist
    if "file" not in df_new.columns:
        df_new["file"] = filename
    
    # Check if file exists
    file_exists = os.path.exists(output_file)
    
    if file_exists:
        try:
            # Load existing data
            existing_df = pd.read_excel(output_file, sheet_name=sheet_name)
            
            # Find rows for this specific file
            file_mask = existing_df["file"] == filename
            
            if file_mask.any():
                # File already has data - ask user what to do
                print(f"\n⚠️  File '{filename}' already has {file_mask.sum()} rows in the output.")
                print("Options:")
                print("  1. Replace existing data for this file")
                print("  2. Append as new rows (duplicate file entries)")
                print("  3. Skip export for this file")
                
                choice = input("Enter choice (1/2/3): ").strip()
                
                if choice == "1":
                    # Remove old rows for this file, keep others
                    existing_df = existing_df[~file_mask]
                    final_df = pd.concat([existing_df, df_new], ignore_index=True)
                    print(f"  Replaced {file_mask.sum()} old rows with {len(df_new)} new rows")
                
                elif choice == "2":
                    # Append new rows (will have duplicate file entries)
                    final_df = pd.concat([existing_df, df_new], ignore_index=True)
                    print(f"  Appended {len(df_new)} new rows (total: {len(final_df)} rows)")
                
                else:  # Choice 3 or invalid
                    print("  Skipping export for this file")
                    return
            else:
                # File not in existing data - just append
                final_df = pd.concat([existing_df, df_new], ignore_index=True)
                print(f"  Appended {len(df_new)} new rows (total: {len(final_df)} rows)")
                
        except Exception as e:
            print(f"Warning: Could not read existing file. Starting fresh. Error: {e}")
            final_df = df_new
    else:
        # File doesn't exist - create new
        final_df = df_new
        print(f"  Created new file with {len(final_df)} rows")
    
    # Write to Excel
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        final_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"✓ Results saved to: {output_file}")
    print(f"  Sheet: {sheet_name}, Total rows: {len(final_df)}")