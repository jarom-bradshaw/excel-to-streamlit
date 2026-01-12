"""Script to create test fixture Excel files."""

import pandas as pd
from pathlib import Path

fixtures_dir = Path(__file__).parent / "fixtures"
fixtures_dir.mkdir(exist_ok=True)

# Sample data with all column types
sample_data = {
    "id": [1, 2, 3, 4, 5],
    "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "age": [25, 30, 35, 28, 32],
    "salary": [50000.50, 60000.75, 70000.00, 55000.25, 65000.50],
    "hire_date": pd.to_datetime(["2020-01-15", "2019-03-20", "2018-06-10", "2021-02-05", "2019-11-30"]),
}

df = pd.DataFrame(sample_data)
df.to_excel(fixtures_dir / "sample_data.xlsx", index=False, engine="openpyxl")

# Sample data without headers (will test auto-generation)
df_no_headers = pd.DataFrame(sample_data)
df_no_headers.to_excel(
    fixtures_dir / "sample_no_headers.xlsx",
    index=False,
    header=False,
    engine="openpyxl",
)

# Sample data without unique primary key
sample_no_pk = {
    "category": ["A", "A", "B", "B", "C"],
    "value": [10, 20, 30, 40, 50],
    "description": ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"],
}

df_no_pk = pd.DataFrame(sample_no_pk)
df_no_pk.to_excel(fixtures_dir / "sample_no_pk.xlsx", index=False, engine="openpyxl")

# Empty sheet
df_empty = pd.DataFrame()
df_empty.to_excel(fixtures_dir / "sample_empty.xlsx", index=False, engine="openpyxl")

print(f"Created test fixtures in {fixtures_dir}")
