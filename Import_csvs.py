import pandas as pd
import sqlite3

# Parameters
csv_files = [
    ("accounts.csv", "accounts"),
    ("products.csv", "products"),
    ("sales_teams.csv", "sales_teams"),
    ("sales_pipeline.csv", "sales_pipeline"),
    ("interactions.csv", "interactions")
]
sqlite_db = "AmericanEquity.db"

# Connect to SQLite (creates file if it doesn't exist)
conn = sqlite3.connect(sqlite_db)

# For each CSV file, import into a table
for csv_file, table_name in csv_files:
    df = pd.read_csv(csv_file)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"Imported {csv_file} into table {table_name}")

conn.close()

conn = sqlite3.connect(sqlite_db)
query = "SELECT * FROM accounts LIMIT 5"
df = pd.read_sql(query, conn)
print(df)
conn.close()