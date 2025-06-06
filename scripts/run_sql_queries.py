import sqlite3
import pandas as pd
from tabulate import tabulate

def display_formatted_results(df, title=""):
    """Display DataFrame with nice formatting"""
    if title:
        print(f"\n{title.upper()}")
    print(tabulate(df.head(), headers='keys', tablefmt='psql', showindex=False))
    if len(df) > 5:
        print(f"\nShowing 5 of {len(df)} rows...")

conn = sqlite3.connect("data/retail.db")

with open("sql/extract_queries.sql", "r") as file:
    queries = [q.strip() for q in file.read().split(';') if q.strip()]
    
    for i, query in enumerate(queries, 1):
        try:
            df = pd.read_sql_query(query, conn)
            display_formatted_results(df, f"Query {i} Results")
            
            # Save each query to Excel
            with pd.ExcelWriter("reports/sales_analysis.xlsx", mode='a' if i>1 else 'w', engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=f"Analysis_{i}", index=False)
                
        except Exception as e:
            print(f"\nError in Query {i}: {str(e)}")
            continue

conn.close()
print("\nAll results saved to 'reports/sales_analysis.xlsx'")