import pandas as pd, numpy as np, random
from faker import Faker
from datetime import datetime, timedelta
from tqdm import tqdm

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# --- PARAMETERS ---
N_CUSTOMERS = 100_000
N_PRODUCTS  = 500
START_DATE  = datetime(2022,1,1)
END_DATE    = datetime(2025,10,31)
CHANNELS    = ["Google Ads","Facebook Ads","LinkedIn","Instagram","Email","YouTube"]

# --- CUSTOMERS ---
print("Generating customers...")
countries = ["USA","Canada","UK","India","Australia","Germany"]
signup_dates = pd.date_range(START_DATE, END_DATE, freq="D")
customers = pd.DataFrame({
    "customer_id": range(1, N_CUSTOMERS+1),
    "email": [fake.email() for _ in range(N_CUSTOMERS)],
    "country": np.random.choice(countries, N_CUSTOMERS, p=[.25,.25,.15,.15,.1,.1]),
    "signup_ts": np.random.choice(signup_dates, N_CUSTOMERS)
})
customers.to_csv("data/customers_large.csv", index=False)

# --- PRODUCTS ---
print("Generating products...")
products = pd.DataFrame({
    "product_id": range(501, 501+N_PRODUCTS),
    "product_name": [f"Product_{i}" for i in range(N_PRODUCTS)],
    "category": np.random.choice(["Electronics","Clothing","Beauty","Home","Sports"], N_PRODUCTS),
    "base_price": np.random.uniform(10,500,N_PRODUCTS).round(2)
})

# --- ORDERS ---
print("Generating orders...")
N_ORDERS = 1_000_000
order_dates = pd.date_range(START_DATE, END_DATE, freq="D")
customer_choices = np.random.choice(customers.customer_id, N_ORDERS)
order_ts = np.random.choice(order_dates, N_ORDERS)
gross = np.random.gamma(shape=2.0, scale=120.0, size=N_ORDERS).round(2)
discount = (gross * np.random.uniform(0,0.2,N_ORDERS)).round(2)
orders = pd.DataFrame({
    "order_id": range(100000, 100000+N_ORDERS),
    "customer_id": customer_choices,
    "order_ts": order_ts,
    "gross": gross,
    "discount": discount
})
orders.to_csv("data/orders_large.csv", index=False)

# --- ORDER ITEMS ---
print("Generating order_items...")
order_items = []
for oid in tqdm(orders.order_id, total=N_ORDERS):
    n_items = np.random.randint(1,4)
    prods = np.random.choice(products.product_id, n_items, replace=False)
    for pid in prods:
        qty = np.random.randint(1,4)
        price = float(products.loc[products.product_id==pid,"base_price"].values[0])
        order_items.append((oid,pid,qty,price))
order_items = pd.DataFrame(order_items, columns=["order_id","product_id","qty","price"])
order_items.to_csv("data/order_items_large.csv", index=False)

# --- MARKETING SPEND ---
print("Generating marketing_spend...")
days = pd.date_range(START_DATE, END_DATE, freq="D")
spend = []
for d in days:
    for ch in CHANNELS:
        base = np.random.normal(1000,300)
        seasonal = 1 + 0.2*np.sin(2*np.pi*(d.timetuple().tm_yday)/365)
        val = max(100, base*seasonal)
        spend.append((d.strftime("%Y-%m-%d"), ch, round(val,2)))
marketing = pd.DataFrame(spend, columns=["day","channel_name","spend"])
marketing.to_csv("data/marketing_spend_large.csv", index=False)

print("✅ Done: Enterprise-scale synthetic data generated.")