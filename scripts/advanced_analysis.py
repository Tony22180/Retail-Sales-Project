import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

conn = sqlite3.connect("data/retail.db")

df = pd.read_sql_query("""
    SELECT 
        Invoice, 
        StockCode, 
        Description, 
        Quantity, 
        InvoiceDate, 
        Price, 
        Customer_ID, 
        Country 
    FROM retail
    WHERE Quantity > 0 AND Price > 0  -- Exclude returns and zero-prices
""", conn, parse_dates=['InvoiceDate'])

analysis_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

def calculate_rfm(df, analysis_date):
    rfm = df.groupby('Customer_ID').agg({
        'InvoiceDate': lambda x: (analysis_date - x.max()).days,
        'Invoice': 'nunique',
        'Price': 'sum'
    }).rename(columns={
        'InvoiceDate': 'Recency',
        'Invoice': 'Frequency',
        'Price': 'Monetary'
    })
    
    rfm['R_Score'] = pd.cut(rfm['Recency'].rank(pct=True)*100, 
                        bins=[0,20,40,60,80,100], 
                        labels=[1,2,3,4,5])
    
    rfm['F_Score'] = pd.cut(rfm['Frequency'].rank(pct=True)*100,
                        bins=[0,20,40,60,80,100],
                        labels=[1,2,3,4,5])
    
    rfm['M_Score'] = pd.cut(rfm['Monetary'].rank(pct=True)*100,
                        bins=[0,20,40,60,80,100],
                        labels=[1,2,3,4,5])
    
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    rfm['Segment'] = 'Green'
    rfm.loc[rfm['RFM_Score'].isin(['555','554','544','545','454']), 'Segment'] = 'Gold'
    rfm.loc[rfm['RFM_Score'].isin(['111','112','113','114']), 'Segment'] = 'At Risk'
    
    return rfm

rfm_results = calculate_rfm(df, analysis_date)
rfm_results.to_excel("reports/rfm_analysis.xlsx")
print("RFM analysis saved to reports/rfm_analysis.xlsx")

# Cohort Analysis
def calculate_cohorts(df):
    df = df[df['Customer_ID'].notna()]
    
    df['CohortMonth'] = df['InvoiceDate'].dt.to_period('M')
    first_purchase = df.groupby('Customer_ID')['InvoiceDate'].min().dt.to_period('M')
    df['Cohort'] = df['Customer_ID'].map(first_purchase)
    
    df['CohortIndex'] = (df['InvoiceDate'].dt.to_period('M') - df['Cohort']).apply(lambda x: x.n)
  
    cohort_data = df.groupby(['Cohort', 'CohortIndex'])['Customer_ID'].nunique().reset_index()
    cohort_counts = cohort_data.pivot(index='Cohort', columns='CohortIndex', values='Customer_ID')
    
    cohort_sizes = cohort_counts.iloc[:, 0]
    retention_matrix = cohort_counts.divide(cohort_sizes, axis=0)
    
    plt.figure(figsize=(12, 8))
    sns.set(font_scale=0.8)
    ax = sns.heatmap(
        retention_matrix, 
        annot=True, 
        fmt='.0%', 
        cmap='YlGnBu',
        mask=retention_matrix.isnull(),
        vmin=0.0,
        vmax=0.5
    )
    ax.set_title('Monthly Cohorts: Customer Retention Rates', fontsize=14)
    ax.set_xlabel('Months Since First Purchase', fontsize=12)
    ax.set_ylabel('Cohort Month', fontsize=12)
    plt.tight_layout()
    plt.savefig("reports/cohort_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    return retention_matrix

cohort_results = calculate_cohorts(df)
print("Cohort analysis saved to reports/cohort_analysis.png")

# Time Series Forecasting
from statsmodels.tsa.arima.model import ARIMA
def forecast_sales(df):
    daily_sales = df.set_index('InvoiceDate').resample('D')['Price'].sum()
    
    model = ARIMA(daily_sales, order=(7,1,0))
    model_fit = model.fit()
    
    forecast = model_fit.forecast(steps=30)
    
    plt.figure(figsize=(12,6))
    daily_sales.plot(label='Historical')
    forecast.plot(label='Forecast')
    plt.title('30-Day Sales Forecast')
    plt.legend()
    plt.savefig("reports/sales_forecast.png")
    plt.close()
    
    return forecast

forecast_results = forecast_sales(df)