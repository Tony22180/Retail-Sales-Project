import sqlite3
import pandas as pd

conn = sqlite3.connect("data/retail.db")
df = pd.read_sql_query("SELECT * FROM retail LIMIT 1", conn)
print("Columns in your database:")
print(df.columns.tolist())
conn.close()