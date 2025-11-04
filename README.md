BizLens — Unified Business KPI & Forecasting Platform

**BizLens** is an end-to-end business intelligence and forecasting platform that unifies KPIs from multiple sources (marketing, sales, operations) into one real-time analytics hub.  
Built using **Python**, **SQL (PostgreSQL)**, and **Power BI**, BizLens helps teams visualize performance, identify trends, and forecast future outcomes.

---

# Key Features

| Category | Description |
|-----------|-------------|
| Data Integration | Extracts and transforms data from Google Ads, Facebook Ads, LinkedIn, Email, and YouTube. |
| KPI Engine | Computes daily metrics for Revenue, Orders, AOV, CAC, ROI, and Conversion Rate. |
| Forecasting | Uses Prophet & Statsmodels to forecast KPIs for the next 30 days. |
| Visualization | Interactive Power BI dashboards for KPI trends, forecast accuracy, and channel comparison. |
| Automation | Python + APScheduler pipeline runs daily ETL and forecasting automatically. |
| Predictive Insights | Machine-learning-driven anomaly detection and performance alerts. |

---

# System Architecture

```mermaid
flowchart LR
A[Data Sources<br>Google Ads / Meta / LinkedIn / Email / YouTube] --> B[Python ETL Scripts]
B --> C[(PostgreSQL Database)]
C --> D[Forecast Models<br>Prophet / Statsmodels / scikit-learn]
D --> E[Power BI Dashboard<br>KPI & Forecast Visualization]
