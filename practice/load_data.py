import pandas as pd
from sqlalchemy import create_engine

# PUT YOUR PASSWORD HERE
YOUR_PASSWORD = "postgres123"  # change this to your actual password

engine = create_engine(
    f"postgresql+psycopg2://postgres:{YOUR_PASSWORD}@localhost:5432/agentic_sql_analyst"
)

customers   = pd.read_csv("customers.csv")
products    = pd.read_csv("products.csv")
orders      = pd.read_csv("orders.csv")
order_items = pd.read_csv("order_items.csv")

customers.to_sql("customers",     engine, if_exists="replace", index=False)
products.to_sql("products",       engine, if_exists="replace", index=False)
orders.to_sql("orders",           engine, if_exists="replace", index=False)
order_items.to_sql("order_items", engine, if_exists="replace", index=False)

print("✅ All data loaded successfully!")