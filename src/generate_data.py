"""Generate realistic synthetic retail data for the analytics project."""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from config import DATA_RAW_DIR


fake = Faker("en_US")
Faker.seed(42)
RNG = np.random.default_rng(42)

STATES_BY_REGION = {
    "Northeast": ["NY", "NJ", "MA", "PA", "CT"],
    "South": ["TX", "FL", "GA", "NC", "VA"],
    "Midwest": ["IL", "OH", "MI", "MN", "WI"],
    "West": ["CA", "WA", "CO", "AZ", "OR"],
}

CATEGORIES = {
    "Electronics": ["Phones", "Computers", "Accessories", "Audio"],
    "Clothing": ["Men", "Women", "Shoes", "Outerwear"],
    "Beauty": ["Skincare", "Makeup", "Fragrance", "Haircare"],
    "Home": ["Kitchen", "Decor", "Furniture", "Bedding"],
    "Grocery": ["Snacks", "Beverages", "Pantry", "Frozen"],
    "Sports": ["Fitness", "Outdoor", "Team Sports", "Footwear"],
    "Books": ["Fiction", "Nonfiction", "Children", "Business"],
}

LOYALTY_TIERS = ["Bronze", "Silver", "Gold", "Platinum"]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "PayPal", "Cash", "Gift Card"]


def random_date(start: date, end: date, size: int) -> list[date]:
    """Generate random dates between start and end."""
    days = (end - start).days
    offsets = RNG.integers(0, days + 1, size=size)
    return [start + timedelta(days=int(offset)) for offset in offsets]


def build_customers(n_customers: int) -> pd.DataFrame:
    """Create customer records with demographics and loyalty tiers."""
    signup_dates = random_date(date(2021, 1, 1), date(2025, 12, 31), n_customers)
    rows = []
    for customer_id in range(1, n_customers + 1):
        gender = RNG.choice(["Female", "Male", "Non-binary"], p=[0.51, 0.47, 0.02])
        first_name = fake.first_name_female() if gender == "Female" else fake.first_name_male()
        last_name = fake.last_name()
        state = RNG.choice(sum(STATES_BY_REGION.values(), []))
        rows.append(
            {
                "customer_id": customer_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": f"{first_name}.{last_name}{customer_id}@example.com".lower(),
                "gender": gender,
                "age": int(np.clip(RNG.normal(39, 13), 18, 82)),
                "city": fake.city(),
                "state": state,
                "signup_date": signup_dates[customer_id - 1],
                "loyalty_tier": RNG.choice(LOYALTY_TIERS, p=[0.48, 0.30, 0.16, 0.06]),
            }
        )
    return pd.DataFrame(rows)


def build_products(n_products: int) -> pd.DataFrame:
    """Create a product catalog with category-specific price behavior."""
    price_ranges = {
        "Electronics": (35, 1200),
        "Clothing": (12, 180),
        "Beauty": (8, 130),
        "Home": (15, 650),
        "Grocery": (2, 45),
        "Sports": (10, 350),
        "Books": (6, 55),
    }
    rows = []
    category_names = list(CATEGORIES)
    for product_id in range(1, n_products + 1):
        category = RNG.choice(category_names, p=[0.14, 0.18, 0.13, 0.15, 0.22, 0.10, 0.08])
        subcategory = RNG.choice(CATEGORIES[category])
        low, high = price_ranges[category]
        unit_price = round(float(RNG.lognormal(np.log((low + high) / 5), 0.55)), 2)
        unit_price = round(float(np.clip(unit_price, low, high)), 2)
        margin_rate = float(RNG.uniform(0.35, 0.68))
        cost = round(unit_price * (1 - margin_rate), 2)
        rows.append(
            {
                "product_id": product_id,
                "product_name": f"{fake.word().title()} {subcategory} {product_id}",
                "category": category,
                "subcategory": subcategory,
                "unit_price": unit_price,
                "cost": max(cost, 0.50),
            }
        )
    return pd.DataFrame(rows)


def build_stores(n_stores: int) -> pd.DataFrame:
    """Create store records across four US sales regions."""
    rows = []
    regions = list(STATES_BY_REGION)
    for store_id in range(1, n_stores + 1):
        region = RNG.choice(regions, p=[0.23, 0.31, 0.21, 0.25])
        state = RNG.choice(STATES_BY_REGION[region])
        rows.append(
            {
                "store_id": store_id,
                "store_name": f"{fake.city()} Market {store_id}",
                "city": fake.city(),
                "state": state,
                "region": region,
            }
        )
    return pd.DataFrame(rows)


def holiday_multiplier(transaction_date: date) -> float:
    """Return a sales intensity multiplier for holiday-heavy periods."""
    month_day = (transaction_date.month, transaction_date.day)
    if transaction_date.month in [11, 12]:
        return 1.75
    if month_day in [(7, 4), (9, 1), (1, 1)]:
        return 1.35
    if transaction_date.month in [5, 6, 8]:
        return 1.12
    return 1.0


def build_transactions(
    customers: pd.DataFrame,
    products: pd.DataFrame,
    stores: pd.DataFrame,
    n_transactions: int,
) -> pd.DataFrame:
    """Create transaction records with repeat shoppers and weighted products."""
    customer_weights = RNG.pareto(2.2, len(customers)) + 0.25
    customer_weights = customer_weights / customer_weights.sum()

    product_weights = RNG.zipf(1.7, len(products)).astype(float)
    product_weights = product_weights / product_weights.sum()

    store_weights = RNG.uniform(0.6, 1.4, len(stores))
    store_weights = store_weights / store_weights.sum()

    candidate_dates = np.array(random_date(date(2023, 1, 1), date(2025, 12, 31), n_transactions * 2))
    date_weights = np.array([holiday_multiplier(d) for d in candidate_dates], dtype=float)
    date_weights = date_weights / date_weights.sum()
    chosen_dates = RNG.choice(candidate_dates, size=n_transactions, replace=True, p=date_weights)

    customer_ids = RNG.choice(customers["customer_id"].to_numpy(), n_transactions, p=customer_weights)
    product_ids = RNG.choice(products["product_id"].to_numpy(), n_transactions, p=product_weights)
    store_ids = RNG.choice(stores["store_id"].to_numpy(), n_transactions, p=store_weights)

    product_lookup = products.set_index("product_id")
    base_prices = product_lookup.loc[product_ids, "unit_price"].to_numpy()
    costs = product_lookup.loc[product_ids, "cost"].to_numpy()

    discount_options = np.array([0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30])
    discounts = RNG.choice(discount_options, n_transactions, p=[0.42, 0.18, 0.16, 0.10, 0.08, 0.04, 0.02])
    quantity_lambda = 1.15 + discounts * 5.0 + np.array([holiday_multiplier(d) - 1 for d in chosen_dates])
    quantities = np.clip(RNG.poisson(quantity_lambda) + 1, 1, 12)

    unit_prices = np.round(base_prices * RNG.normal(1.0, 0.025, n_transactions), 2)
    unit_prices = np.maximum(unit_prices, 0.50)

    transactions = pd.DataFrame(
        {
            "transaction_id": np.arange(1, n_transactions + 1),
            "customer_id": customer_ids,
            "product_id": product_ids,
            "store_id": store_ids,
            "transaction_date": chosen_dates,
            "quantity": quantities.astype(int),
            "unit_price": unit_prices,
            "discount_percent": discounts,
            "payment_method": RNG.choice(PAYMENT_METHODS, n_transactions, p=[0.38, 0.25, 0.18, 0.12, 0.07]),
        }
    )

    revenue = transactions["quantity"].to_numpy() * transactions["unit_price"].to_numpy() * (1 - transactions["discount_percent"].to_numpy())
    profit = revenue - transactions["quantity"].to_numpy() * costs
    transactions["revenue"] = np.round(revenue, 2)
    transactions["profit"] = np.round(profit, 2)
    return transactions.sort_values("transaction_date").reset_index(drop=True)


def generate_all(
    n_customers: int = 5_000,
    n_products: int = 300,
    n_stores: int = 50,
    n_transactions: int = 50_000,
    output_dir: Path = DATA_RAW_DIR,
) -> None:
    """Generate all project CSV files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    customers = build_customers(n_customers)
    products = build_products(n_products)
    stores = build_stores(n_stores)
    transactions = build_transactions(customers, products, stores, n_transactions)

    customers.to_csv(output_dir / "customers.csv", index=False)
    products.to_csv(output_dir / "products.csv", index=False)
    stores.to_csv(output_dir / "stores.csv", index=False)
    transactions.to_csv(output_dir / "transactions.csv", index=False)
    print(f"Generated CSV files in {output_dir}")


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="Generate synthetic retail analytics data.")
    parser.add_argument("--transactions", type=int, default=50_000)
    parser.add_argument("--customers", type=int, default=5_000)
    parser.add_argument("--products", type=int, default=300)
    parser.add_argument("--stores", type=int, default=50)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate_all(args.customers, args.products, args.stores, args.transactions)
