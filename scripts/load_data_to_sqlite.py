import pandas as pd
import sqlite3

df = pd.read_excel("data/online_retail_II.xlsx", sheet_name="Year 2009-2010")

df = df.dropna(subset=["Customer ID", "Invoice", "Description", "Country"])

df.columns = [col.strip().replace(" ", "_").replace("(", "").replace(")", "") for col in df.columns]

conn = sqlite3.connect("data/retail.db")

df.to_sql("retail", conn, if_exists="replace", index=False)

print("Data loaded to SQLite database.")
conn.close()