#!/usr/bin/env python3
import pandas as pd
from datetime import datetime

# Read the CSV file
csv_file = "smi_total_return_2000_2024.csv"
df = pd.read_csv(csv_file, index_col=0, parse_dates=True)

# Convert the Total Return column to a dictionary
smi_dict = {}
for date, row in df.iterrows():
    date_str = date.strftime('%Y-%m-%d')
    value = round(row['SMI_Total_Return_Synthetic'], 2)
    smi_dict[date_str] = value

# Generate Python code
python_code = []
python_code.append("# This file was auto-generated from CSV data.")
python_code.append("# Data source: Yahoo Finance ^SSMI (Swiss Market Index)")
python_code.append(f"# Period: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')} (complete, no gaps)")
python_code.append("# Note: Values are SMI Total Return Index (synthetic, with estimated dividends).")
python_code.append("import pandas as pd")
python_code.append("")
python_code.append("smi = {")

# Add dictionary entries
for date_str, value in smi_dict.items():
    python_code.append(f"    '{date_str}': {value},")

python_code.append("}")
python_code.append("")
python_code.append("")
python_code.append("def analyze_smic():")
python_code.append("    print(f\"Loaded {len(smi)} months of data.\")")
python_code.append("    ")
python_code.append("    dates = sorted(smi.keys())")
python_code.append("    if not dates:")
python_code.append("        print(\"No data available.\")")
python_code.append("        return")
python_code.append("")
python_code.append("    first_date = dates[0]")
python_code.append("    last_date = dates[-1]")
python_code.append("    start_price = smi[first_date]")
python_code.append("    end_price = smi[last_date]")
python_code.append("    ")
python_code.append("    total_return = ((end_price - start_price) / start_price) * 100")
python_code.append("    ")
python_code.append("    print(\"-\" * 40)")
python_code.append("    print(f\"Start Date: {first_date} | Value: {start_price}\")")
python_code.append("    print(f\"End Date:   {last_date} | Value: {end_price}\")")
python_code.append("    print(f\"Total Return (Abs): {total_return:.2f}%\")")
python_code.append("    print(\"-\" * 40)")
python_code.append("    ")
python_code.append("    # Example: Calculate monthly returns")
python_code.append("    print(\"\\nRecent Monthly Performance:\")")
python_code.append("    recent_dates = dates[-5:] # Last 5 months")
python_code.append("    for i in range(1, len(recent_dates)):")
python_code.append("        curr_date = recent_dates[i]")
python_code.append("        prev_date = recent_dates[i-1]")
python_code.append("        curr_val = smi[curr_date]")
python_code.append("        prev_val = smi[prev_date]")
python_code.append("        ")
python_code.append("        pct_change = ((curr_val - prev_val) / prev_val) * 100")
python_code.append("        print(f\"{curr_date}: {curr_val:>8.2f} ({pct_change:>+6.2f}%)\")")
python_code.append("")
python_code.append("if __name__ == \"__main__\":")
python_code.append("    analyze_smic()")
python_code.append("")

# Write to file
output_file = "smic2.py"
with open(output_file, 'w') as f:
    f.write('\n'.join(python_code))

print(f"✅ Generated {output_file} from {csv_file}")
print(f"   Records: {len(smi_dict)} months")
print(f"   Date range: {list(smi_dict.keys())[0]} to {list(smi_dict.keys())[-1]}")