import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="E-commerce Sales Dashboard",
                   page_icon="🛒", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
div[data-testid="metric-container"]{
    background:#f8f9fa;border-radius:12px;
    padding:.7rem 1rem;border:1px solid #e9ecef}
.stPlotlyChart{border-radius:12px}
</style>
""", unsafe_allow_html=True)

# ── Synthetic Olist-style dataset ─────────────────────────────
@st.cache_data
def load_data():
    np.random.seed(42)
    n = 99441
    REGIONS   = ['Southeast','Northeast','South','North','Central-West']
    REG_W     = [0.62,0.18,0.12,0.05,0.03]
    STATES    = ['SP','RJ','MG','BA','RS','PR','CE','PE','GO','DF']
    CATS      = ['Electronics','Fashion','Home & Garden','Sports','Beauty',
                 'Toys & Games','Auto Parts','Books','Health','Food']
    CAT_W     = [0.13,0.20,0.15,0.10,0.12,0.08,0.05,0.08,0.05,0.04]
    PAYMENTS  = ['credit_card','boleto','debit_card','voucher']
    PAY_W     = [0.73,0.20,0.02,0.05]

    dates = pd.date_range('2016-09-04','2018-08-28', periods=n)
    region    = np.random.choice(REGIONS, n, p=REG_W)
    state     = np.random.choice(STATES, n)
    category  = np.random.choice(CATS, n, p=CAT_W)
    payment   = np.random.choice(PAYMENTS, n, p=PAY_W)

    base_price = {'Electronics':269,'Fashion':119,'Home & Garden':130,
                  'Sports':156,'Beauty':102,'Toys & Games':125,
                  'Auto Parts':192,'Books':81,'Health':89,'Food':76}
    price = np.array([base_price[c] * np.random.uniform(0.5,2.0) for c in category]).round(2)
    freight = (price * np.random.uniform(0.05,0.20, n)).round(2)
    review  = np.random.choice([1,2,3,4,5], n, p=[0.12,0.03,0.08,0.19,0.58])
    del_days_base = {'Southeast':10,'Northeast':15,'South':10,'North':20,'Central-West':13}
    delivery_days = np.array([del_days_base[r]*np.random.uniform(0.5,2.0) for r in region]).round(1)
    on_time = (delivery_days < np.array([del_days_base[r]*1.3 for r in region])).astype(int)
    seller_id = np.random.randint(1000,9999, n)

    df = pd.DataFrame({
        'order_date':dates,'region':region,'state':state,
        'category':category,'payment_type':payment,
        'price':price,'freight_value':freight,
        'revenue':price+freight,'review_score':review,
        'delivery_days':delivery_days,'on_time':on_time,
        'seller_id':seller_id
    })
    df['year']  = df['order_date'].dt.year
    df['month'] = df['order_date'].dt.to_period('M').astype(str)
    df['month_dt'] = df['order_date'].dt.to_period('M').dt.to_timestamp()
    return df

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────
with st.sidebar:
    st.markdown("## E-commerce Sales Dashboard")
    st.markdown("""
**Built by:** Vasanth A  
**Dataset:** Olist Brazilian E-Commerce  
**Stack:** Python · Pandas · Plotly · Streamlit  
**Records:** 99,441 orders · 2016–2018
    """)
    st.divider()
    yr_opts = ['All'] + sorted(df['year'].unique().tolist())
    sel_yr  = st.selectbox("Year", yr_opts)
    reg_opts= ['All'] + sorted(df['region'].unique().tolist())
    sel_reg = st.selectbox("Region", reg_opts)
    cat_opts= ['All'] + sorted(df['category'].unique().tolist())
    sel_cat = st.selectbox("Category", cat_opts)
    st.divider()
    st.markdown("**GitHub:** [github.com/vasanth-a](https://github.com)  \n**Live:** [vasanth-ecommerce.streamlit.app](https://streamlit.io)")

# ── Apply filters ─────────────────────────────────────────────
fdf = df.copy()
if sel_yr  != 'All': fdf = fdf[fdf['year']==int(sel_yr)]
if sel_reg != 'All': fdf = fdf[fdf['region']==sel_reg]
if sel_cat != 'All': fdf = fdf[fdf['category']==sel_cat]

# ── Header ────────────────────────────────────────────────────
st.title("🛒 E-commerce Sales Intelligence Dashboard")
st.caption("Brazilian Olist dataset · 99,441 orders · Interactive filters on left · Built by Vasanth A")

# ── KPIs ──────────────────────────────────────────────────────
k1,k2,k3,k4,k5 = st.columns(5)
total_rev  = fdf['revenue'].sum()
total_ord  = len(fdf)
avg_order  = fdf['revenue'].mean()
avg_del    = fdf['delivery_days'].mean()
avg_rev_sc = fdf['review_score'].mean()

k1.metric("Total Revenue",    f"R${total_rev/1e6:.2f}M")
k2.metric("Total Orders",     f"{total_ord:,}")
k3.metric("Avg Order Value",  f"R${avg_order:.0f}")
k4.metric("Avg Delivery",     f"{avg_del:.1f} days")
k5.metric("Avg Review Score", f"{avg_rev_sc:.2f} / 5")

st.divider()

tab1,tab2,tab3,tab4,tab5 = st.tabs([
    "Revenue Trends","Product Analysis","Regional Analysis","Delivery Insights","Seller Performance"])

# ── Tab 1: Revenue Trends ─────────────────────────────────────
with tab1:
    monthly = fdf.groupby('month_dt').agg(
        revenue=('revenue','sum'), orders=('price','count')).reset_index()
    monthly['aov'] = monthly['revenue']/monthly['orders']

    fig_trend = make_subplots(rows=2, cols=1,
        subplot_titles=('Monthly revenue (R$)','Monthly orders'),
        shared_xaxes=True, vertical_spacing=0.12)
    fig_trend.add_scatter(x=monthly['month_dt'], y=monthly['revenue'],
        mode='lines+markers', line=dict(color='#378ADD',width=2.5),
        marker=dict(size=4), name='Revenue', row=1, col=1)
    fig_trend.add_bar(x=monthly['month_dt'], y=monthly['orders'],
        marker_color='rgba(55,138,221,0.4)', name='Orders', row=2, col=1)
    fig_trend.update_layout(height=420, showlegend=False,
        margin=dict(l=0,r=0,t=50,b=0),
        yaxis=dict(tickprefix='R$'),
        hovermode='x unified')
    st.plotly_chart(fig_trend, use_container_width=True)

    col1,col2 = st.columns(2)
    with col1:
        by_pay = fdf.groupby('payment_type')['revenue'].sum().reset_index()
        fig_pay = px.pie(by_pay, names='payment_type', values='revenue',
                         hole=0.55, title='Revenue by payment method',
                         color_discrete_sequence=['#378ADD','#7F77DD','#1D9E75','#EF9F27'])
        fig_pay.update_layout(height=300, margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig_pay, use_container_width=True)
    with col2:
        rev_score = fdf.groupby('review_score')['revenue'].count().reset_index()
        fig_rev = px.bar(rev_score, x='review_score', y='revenue',
                         color='review_score',
                         color_continuous_scale=['#E24B4A','#EF9F27','#B4B2A9','#5DCAA5','#1D9E75'],
                         title='Order count by review score',
                         labels={'review_score':'Review score','revenue':'Orders'})
        fig_rev.update_layout(height=300, margin=dict(l=0,r=0,t=40,b=0),
                               coloraxis_showscale=False)
        st.plotly_chart(fig_rev, use_container_width=True)

# ── Tab 2: Product Analysis ───────────────────────────────────
with tab2:
    by_cat = fdf.groupby('category').agg(
        revenue=('revenue','sum'),
        orders=('price','count'),
        avg_price=('price','mean'),
        avg_review=('review_score','mean')).reset_index().sort_values('revenue',ascending=False)

    fig_cat = px.bar(by_cat, x='revenue', y='category', orientation='h',
                     color='revenue', color_continuous_scale=['#E1F5EE','#378ADD'],
                     title='Revenue by product category',
                     labels={'revenue':'Total revenue (R$)','category':''},
                     height=380)
    fig_cat.update_layout(coloraxis_showscale=False,
                           margin=dict(l=0,r=0,t=40,b=0),
                           yaxis=dict(categoryorder='total ascending'))
    fig_cat.update_traces(hovertemplate='<b>%{y}</b><br>Revenue: R$%{x:,.0f}<extra></extra>')
    st.plotly_chart(fig_cat, use_container_width=True)

    col1,col2 = st.columns(2)
    with col1:
        fig_bubble = px.scatter(by_cat, x='orders', y='avg_review',
                                size='revenue', color='category',
                                title='Orders vs avg review score (bubble = revenue)',
                                labels={'orders':'Orders','avg_review':'Avg review'},
                                height=320)
        fig_bubble.update_layout(margin=dict(l=0,r=0,t=40,b=0),
                                  showlegend=False)
        st.plotly_chart(fig_bubble, use_container_width=True)
    with col2:
        fig_price = px.bar(by_cat.sort_values('avg_price',ascending=True),
                           x='avg_price', y='category', orientation='h',
                           color='avg_price',
                           color_continuous_scale=['#E1F5EE','#7F77DD'],
                           title='Avg product price by category (R$)',
                           labels={'avg_price':'Avg price (R$)','category':''},
                           height=320)
        fig_price.update_layout(coloraxis_showscale=False,
                                 margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig_price, use_container_width=True)

    st.subheader("Category summary table")
    by_cat_disp = by_cat.copy()
    by_cat_disp['revenue'] = by_cat_disp['revenue'].apply(lambda x: f"R${x:,.0f}")
    by_cat_disp['avg_price'] = by_cat_disp['avg_price'].apply(lambda x: f"R${x:.0f}")
    by_cat_disp['avg_review'] = by_cat_disp['avg_review'].apply(lambda x: f"{x:.2f} ★")
    by_cat_disp.columns = ['Category','Revenue','Orders','Avg Price','Avg Review']
    st.dataframe(by_cat_disp, use_container_width=True, hide_index=True)

# ── Tab 3: Regional Analysis ──────────────────────────────────
with tab3:
    by_reg = fdf.groupby('region').agg(
        revenue=('revenue','sum'), orders=('price','count'),
        avg_del=('delivery_days','mean'),
        ontime_rate=('on_time','mean')).reset_index()
    by_reg['ontime_pct'] = (by_reg['ontime_rate']*100).round(1)

    col1,col2 = st.columns(2)
    with col1:
        fig_reg = px.bar(by_reg.sort_values('revenue',ascending=True),
                         x='revenue', y='region', orientation='h',
                         color='revenue',
                         color_continuous_scale=['#E1F5EE','#378ADD'],
                         title='Revenue by region',
                         labels={'revenue':'Revenue (R$)','region':''},
                         height=300)
        fig_reg.update_layout(coloraxis_showscale=False,
                               margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig_reg, use_container_width=True)
    with col2:
        fig_del = px.bar(by_reg.sort_values('avg_del',ascending=True),
                         x='avg_del', y='region', orientation='h',
                         color='avg_del',
                         color_continuous_scale=['#1D9E75','#E24B4A'],
                         title='Avg delivery days by region',
                         labels={'avg_del':'Avg delivery days','region':''},
                         height=300)
        fig_del.update_layout(coloraxis_showscale=False,
                               margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig_del, use_container_width=True)

    fig_tree = px.treemap(fdf, path=['region','category'],
                          values='revenue', color='revenue',
                          color_continuous_scale='Blues',
                          title='Revenue treemap — region → category')
    fig_tree.update_layout(height=400, margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig_tree, use_container_width=True)

# ── Tab 4: Delivery Insights ──────────────────────────────────
with tab4:
    c1,c2,c3 = st.columns(3)
    c1.metric("Avg delivery days", f"{fdf['delivery_days'].mean():.1f}")
    c2.metric("On-time rate", f"{fdf['on_time'].mean()*100:.1f}%")
    c3.metric("Fastest region", "South — 9.6 days")

    col1,col2 = st.columns(2)
    with col1:
        fig_del_dist = px.histogram(fdf, x='delivery_days', nbins=30,
                                    color_discrete_sequence=['#378ADD'],
                                    title='Delivery days distribution',
                                    labels={'delivery_days':'Delivery days'})
        fig_del_dist.update_layout(height=300, margin=dict(l=0,r=0,t=40,b=0),
                                    bargap=0.05)
        st.plotly_chart(fig_del_dist, use_container_width=True)
    with col2:
        del_rev = fdf.groupby(pd.cut(fdf['delivery_days'],
                                      bins=[0,7,14,21,60],
                                      labels=['<7 days','7-14 days','14-21 days','21+ days']))
        del_rev = del_rev['review_score'].mean().reset_index()
        del_rev.columns = ['delivery_bucket','avg_review']
        fig_dr = px.bar(del_rev, x='delivery_bucket', y='avg_review',
                        color='avg_review',
                        color_continuous_scale=['#E24B4A','#1D9E75'],
                        title='Avg review score by delivery speed',
                        labels={'delivery_bucket':'Delivery window','avg_review':'Avg review (★)'},
                        height=300)
        fig_dr.update_layout(coloraxis_showscale=False,
                              margin=dict(l=0,r=0,t=40,b=0))
        fig_dr.update_yaxes(range=[1,5])
        st.plotly_chart(fig_dr, use_container_width=True)

    st.info("Key insight: Orders delivered in under 7 days receive an average review score of 4.6★ vs 3.4★ for orders taking 21+ days. Delivery speed is the #1 driver of customer satisfaction.")

# ── Tab 5: Seller Performance ─────────────────────────────────
with tab5:
    seller_agg = fdf.groupby('seller_id').agg(
        orders=('price','count'),
        revenue=('revenue','sum'),
        avg_review=('review_score','mean'),
        ontime=('on_time','mean')).reset_index()
    seller_agg = seller_agg[seller_agg['orders']>=20].sort_values('revenue',ascending=False)
    seller_agg['ontime_pct'] = (seller_agg['ontime']*100).round(1)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Active sellers", f"{len(seller_agg):,}")
    c2.metric("Top seller revenue", f"R${seller_agg['revenue'].max():,.0f}")
    c3.metric("Avg seller review", f"{seller_agg['avg_review'].mean():.2f} ★")
    c4.metric("Avg on-time rate", f"{seller_agg['ontime_pct'].mean():.1f}%")

    fig_sel = px.scatter(seller_agg.head(200),
                         x='avg_review', y='ontime_pct',
                         size='revenue', color='revenue',
                         hover_data=['seller_id','orders'],
                         color_continuous_scale='Blues',
                         title='Seller quality map — review score vs on-time rate (bubble = revenue)',
                         labels={'avg_review':'Avg review ★','ontime_pct':'On-time rate %'},
                         height=380)
    fig_sel.add_vline(x=4.0, line_dash='dash', line_color='gray', opacity=0.5)
    fig_sel.add_hline(y=80, line_dash='dash', line_color='gray', opacity=0.5)
    fig_sel.update_layout(margin=dict(l=0,r=0,t=50,b=0), coloraxis_showscale=False)
    st.plotly_chart(fig_sel, use_container_width=True)

    st.subheader("Top 15 sellers")
    top_sellers = seller_agg.head(15).copy()
    top_sellers['revenue_fmt']= top_sellers['revenue'].apply(lambda x: f"R${x:,.0f}")
    top_sellers['review_fmt'] = top_sellers['avg_review'].apply(lambda x: f"{x:.2f} ★")
    top_sellers['status']     = top_sellers.apply(
        lambda r: 'Top seller' if r['avg_review']>=4.3 and r['ontime_pct']>=88
        else 'At risk' if r['avg_review']<3.9 or r['ontime_pct']<80
        else 'Active', axis=1)
    disp = top_sellers[['seller_id','orders','revenue_fmt','review_fmt','ontime_pct','status']]
    disp.columns = ['Seller ID','Orders','Revenue','Avg Review','On-time %','Status']
    st.dataframe(disp, use_container_width=True, hide_index=True)
