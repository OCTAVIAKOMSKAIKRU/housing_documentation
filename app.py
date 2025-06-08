# ─── app.py ─────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import os
from scraper.scraper import Property24Scraper
from utils.yield_calc import calculate_gross_yield
from utils.map_utils import create_map

st.set_page_config(page_title="Property24 Listings Dashboard", layout="wide")
st.title("🏠 Property24 Listings Dashboard")

# Path to save/load scraped data
DATA_FILE = "data/property24_listings.csv"
os.makedirs("data", exist_ok=True)

# Auto-delete broken CSV
if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) == 0:
    os.remove(DATA_FILE)

# Load existing data or scrape if CSV missing or empty
if os.path.exists(DATA_FILE):
    st.info("🔄 Loading existing data...")
    df = pd.read_csv(DATA_FILE)
else:
    with st.spinner("⏳ Scraping Property24... This may take a few seconds..."):
        scraper = Property24Scraper(
            base_url="https://www.property24.com/for-sale/advanced-search/results?sp=cid%3d767%2c3%2c7%2c8%2c5%26pf%3d300000%26pt%3d700000&PropertyCategory=House%2cApartmentOrFlat",
            start_page=1,
            end_page=10  # Limit for test speed
        )
        df = scraper.scrape()
        if not df.empty:
            df.to_csv(DATA_FILE, index=False)
            st.success(f"✅ Scraped and saved {len(df)} listings.")
        else:
            st.error("❌ No data scraped. Check connection or scraping logic.")
            df = pd.DataFrame()  # Prevent downstream errors

# Add dummy rent and yield if column exists
if 'MonthlyRent' in df.columns:
    df['Yield%'] = df.apply(lambda row: calculate_gross_yield(row.Price, row.MonthlyRent), axis=1)
else:
    df['MonthlyRent'] = None
    df['Yield%'] = None

# Suburb filter with protection
if 'Suburb' in df.columns:
    suburbs = sorted(df['Suburb'].dropna().unique())
    selected = st.sidebar.multiselect("Filter by Suburb:", options=suburbs, default=suburbs)
    df_filtered = df[df['Suburb'].isin(selected)] if selected else df
else:
    st.error("❌ 'Suburb' column missing. Check scraper parsing.")
    df_filtered = df

# Clean up data for sorting
df_filtered = df_filtered[df_filtered['Price'].notnull()]
sort_option = st.sidebar.radio("Sort by:", ("Price", "Yield%"))
if sort_option == "Price":
    df_filtered = df_filtered.sort_values(by="Price", ascending=True)
else:
    df_filtered = df_filtered.sort_values(by="Yield%", ascending=False, na_position='last')

# Show data
if not df_filtered.empty:
    st.subheader(f"📊 Listings Found: {len(df_filtered)}")
    st.dataframe(df_filtered[['Title','Price','Suburb','City','Bedrooms','Bathrooms','Parking','Yield%']])
else:
    st.warning("⚠️ No listings to show. Try re-running the scraper.")

# Map
if st.button("🗺 Show Map of Listings") and not df_filtered.empty:
    m = create_map(df_filtered)
    st.components.v1.html(m._repr_html_(), height=600, scrolling=True)

# Download CSV
if not df_filtered.empty:
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Download CSV", data=csv_data, file_name="property24_listings.csv", mime="text/csv")