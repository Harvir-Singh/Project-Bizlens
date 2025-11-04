# scripts/forecast_revenue.py
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Try to import Prophet or fallback to ARIMA
try:
    from prophet import Prophet
    MODEL = "prophet"
except ImportError:
    from statsmodels.tsa.arima.model import ARIMA
    MODEL = "arima"

from sklearn.metrics import mean_absolute_percentage_error
import numpy as np

# -------------------- CONFIG & CONNECTION --------------------
load_dotenv()

PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DATABASE = os.getenv("PG_DATABASE")

engine = create_engine(
    f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
)

print(f"🚀 Starting revenue forecasting using {MODEL.upper()} model...")

# -------------------- 1️⃣ Load Historical Data --------------------
with engine.connect() as conn:
    df = pd.read_sql("SELECT day, revenue FROM v_kpi_daily ORDER BY day", conn)

df = df.rename(columns={"day": "ds", "revenue": "y"})
df["ds"] = pd.to_datetime(df["ds"])
df = df[df["y"].notnull()]

print(f"✅ Loaded {len(df)} days of historical revenue data.")

# -------------------- 2️⃣ Train/Test Split --------------------
train = df.iloc[:-14]
test = df.iloc[-14:]

# -------------------- 3️⃣ Fit Model --------------------
if MODEL == "prophet":
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
        interval_width=0.9
    )
    model.fit(train)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    forecast = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]
else:
    model = ARIMA(train["y"], order=(5,1,1)).fit()
    pred = model.get_forecast(steps=30)
    forecast = pd.DataFrame({
        "ds": pd.date_range(df["ds"].iloc[-1], periods=30, freq="D"),
        "yhat": pred.predicted_mean,
        "yhat_lower": pred.conf_int()["lower y"],
        "yhat_upper": pred.conf_int()["upper y"]
    })

# -------------------- 4️⃣ Evaluate Backtest --------------------
try:
    preds = forecast.set_index("ds").join(test.set_index("ds"), how="inner")
    mape = mean_absolute_percentage_error(preds["y"], preds["yhat"])
    smape = 100 * np.mean(2 * np.abs(preds["yhat"] - preds["y"]) / (np.abs(preds["yhat"]) + np.abs(preds["y"])))
    print(f"📊 Backtest — MAPE: {mape:.3f}, SMAPE: {smape:.3f}")
except Exception:
    mape = None
    smape = None

# -------------------- 5️⃣ Write Forecast to Database --------------------
forecast["mape"] = mape
forecast["smape"] = smape

with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS forecast_daily;"))
    forecast.to_sql("forecast_daily", conn, if_exists="replace", index=False)
print(f"✅ Forecast written to forecast_daily ({len(forecast)} rows).")

# -------------------- 6️⃣ Quick Plot --------------------
try:
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 5))
    plt.plot(df["ds"], df["y"], label="Actual")
    plt.plot(forecast["ds"], forecast["yhat"], label="Forecast")
    plt.fill_between(forecast["ds"], forecast["yhat_lower"], forecast["yhat_upper"], alpha=0.2)
    plt.title("Revenue Forecast")
    plt.legend()
    plt.tight_layout()
    plt.show()
except Exception as e:
    print("⚠️ Plot skipped:", e)

print("Forecast generation complete.")
