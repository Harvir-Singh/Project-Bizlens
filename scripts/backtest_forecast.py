import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_percentage_error
from utils_db import engine

with engine.begin() as conn:
    df = pd.read_sql("SELECT day, revenue FROM v_kpi_daily ORDER BY day", conn)

h = 14  # horizon days
window = 60  # training window
scores = []

for end in range(window, len(df) - h):
    train = df.iloc[end-window:end]
    test = df.iloc[end:end+h]
    m = Prophet(weekly_seasonality=True, yearly_seasonality=True)
    m.fit(train.rename(columns={'day':'ds','revenue':'y'}))
    fut = m.make_future_dataframe(periods=h)
    pred = m.predict(fut).tail(h)
    y_true = test['revenue'].values
    y_pred = pred['yhat'].values
    mape = mean_absolute_percentage_error(y_true, y_pred)
    scores.append(mape)

print({'MAPE_mean': float(pd.Series(scores).mean()), 'MAPE_last': float(scores[-1])})
