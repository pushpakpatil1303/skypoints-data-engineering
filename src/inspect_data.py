# eads each Excel file as text to preserve original values, then displays its columns, 
# record count, sample rows and missing-value counts.
from pathlib import Path
import pandas as pd

data_folder = Path(__file__).resolve().parent.parent / "data" / "sample"

for filename in ["AUS.xlsx", "IND.xlsx", "USA.xlsx"]:
    file_path = data_folder / filename

    df = pd.read_excel(file_path, dtype=str)

    print(f"\n{'=' * 50}")
    print(f"File: {filename}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 5 records:")
    print(df.head().to_string(index=False))
    print("\nMissing values:")
    print(df.isna().sum().to_string())
    
    
## Combines member IDs from all three countries and identifies IDs appearing more than once, 
# helping us determine how to handle member identity and country movement.


all_members = []

for filename, id_column, country in [
    ("AUS.xlsx", "Unique ID", "AUS"),
    ("IND.xlsx", "ID", "IND"),
    ("USA.xlsx", "ID", "USA")
]:
    df = pd.read_excel(data_folder / filename, dtype=str)

    df = df.rename(columns={id_column: "MEMBER_ID"})
    df["COUNTRY"] = country

    all_members.append(df[["MEMBER_ID", "COUNTRY"]])

combined_df = pd.concat(all_members, ignore_index=True)

duplicates = combined_df[
    combined_df.duplicated(subset=["MEMBER_ID"], keep=False)
]

print("\nDuplicate Member IDs Across Countries:")
print(duplicates.sort_values("MEMBER_ID").to_string(index=False))


