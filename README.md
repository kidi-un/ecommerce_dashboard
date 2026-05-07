# E-commerce Sales Intelligence Dashboard

**Power BI-style sales dashboard** built by Vasanth A (AI & Data Science, 2026 batch)

## Live Demo
[Open the app](https://vasanth-ecommerce.streamlit.app)

## What it does
- Revenue trend analysis — monthly revenue and orders across 2016–2018
- Product analysis — revenue by category, avg price, review score bubble chart
- Regional analysis — treemap of region → category revenue breakdown
- Delivery insights — delivery speed vs review score correlation
- Seller performance — quality scatter plot (review vs on-time rate)
- Interactive sidebar filters — year, region, category — all charts update live

## Tech stack
| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| Charts | Plotly Express + Graph Objects |
| Data | Pandas (Olist-style synthetic, 99,441 orders) |
| Deploy | Streamlit Cloud (free) |

## Real dataset upgrade
Download the real Olist dataset from Kaggle:
kaggle.com/datasets/olistbr/brazilian-ecommerce
Then replace the generate_data() function with pd.read_csv() calls.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (2 minutes)
1. Push to GitHub repo `ecommerce-sales-dashboard`
2. share.streamlit.io → connect repo → app.py → Deploy

## Resume line
> "Built an E-commerce Sales Intelligence Dashboard — 99K+ orders, revenue trends, regional analysis, seller performance, interactive filters — deployed live at [url]"
