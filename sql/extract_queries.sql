--1 Total Revenue with Currency Formatting
SELECT 
    '$' || ROUND(SUM(Quantity * Price), 2) AS total_revenue,
    COUNT(DISTINCT Invoice) AS total_transactions,
    ROUND(SUM(Quantity * Price) / COUNT(DISTINCT Invoice), 2) AS avg_order_value
FROM retail;

--2 Top 10 Products with Revenue and Margin Analysis
SELECT 
    StockCode,
    Description,
    SUM(Quantity) AS total_units_sold,
    '$' || ROUND(SUM(Quantity * Price), 2) AS total_revenue,
    ROUND(SUM(Quantity * Price) / SUM(Quantity), 2) AS avg_unit_price,
    RANK() OVER (ORDER BY SUM(Quantity * Price) DESC) AS revenue_rank
FROM retail
GROUP BY StockCode, Description
ORDER BY total_revenue DESC
LIMIT 10;

--3 Customer RFM Analysis (Recency, Frequency, Monetary)
WITH rfm_data AS (
    SELECT
        Customer_ID,
        MAX(InvoiceDate) AS last_purchase_date,
        COUNT(DISTINCT Invoice) AS purchase_count,
        SUM(Quantity * Price) AS total_spend
    FROM retail
    WHERE Customer_ID IS NOT NULL
    GROUP BY Customer_ID
)
SELECT
    Customer_ID,
    last_purchase_date,
    purchase_count,
    '$' || ROUND(total_spend, 2) AS total_spend,
    CASE 
        WHEN purchase_count > 10 THEN 'VIP'
        WHEN purchase_count > 5 THEN 'Loyal'
        ELSE 'Regular'
    END AS customer_segment
FROM rfm_data
ORDER BY total_spend DESC;

--4 Monthly Sales Trend with YoY Comparison
SELECT 
    strftime('%Y-%m', InvoiceDate) AS month,
    '$' || ROUND(SUM(Quantity * Price), 2) AS revenue,
    ROUND(SUM(Quantity * Price) / LAG(SUM(Quantity * Price), 12) OVER (ORDER BY strftime('%Y-%m', InvoiceDate)) - 1, 2) AS yoy_growth
FROM retail
GROUP BY month
ORDER BY month;

--5 Product Return Rate Analysis
SELECT 
    Description,
    SUM(CASE WHEN Quantity < 0 THEN ABS(Quantity) ELSE 0 END) AS returned_units,
    SUM(CASE WHEN Quantity > 0 THEN Quantity ELSE 0 END) AS sold_units,
    ROUND(SUM(CASE WHEN Quantity < 0 THEN ABS(Quantity) ELSE 0 END) * 100.0 / 
          NULLIF(SUM(CASE WHEN Quantity > 0 THEN Quantity ELSE 0 END), 0), 2) AS return_rate_percent
FROM retail
GROUP BY Description
HAVING sold_units > 100
ORDER BY return_rate_percent DESC;