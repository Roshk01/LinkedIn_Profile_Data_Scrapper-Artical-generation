import streamlit as st
import pandas as pd

# import your scraping function
from function import scrape_linkedin_profiles

st.set_page_config(page_title="LinkedIn Scraper", page_icon="🔎", layout="wide")

st.title("🔎 LinkedIn Profile Scraper")

# ---- input area: url list ----
urls_text = st.text_area(
    "Paste LinkedIn profile URLs (one per line):",
    height=200,
    placeholder="https://www.linkedin.com/in/example1\nhttps://www.linkedin.com/in/example2"
)

run_button = st.button("Run Scraper")

if run_button:
    # convert text to list
    urls = [line.strip() for line in urls_text.splitlines() if line.strip()]

    if len(urls) == 0:
        st.error("No URLs found.")
        st.stop()

    # call your function
    try:
        st.info("Running scraper...")
        items = scrape_linkedin_profiles(urls)   # <-- your function

        df = pd.DataFrame(items)

        if df.empty:
            st.warning("No data returned. Some profiles might be private / blocked.")
        else:
            st.success(f"Done! Retrieved {len(df)} profiles.")
            st.dataframe(df, use_container_width=True, height=500)  # scrollable

            # Download button
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download CSV",
                csv,
                file_name="linkedin_profiles.csv",
                mime="text/csv"
            )
    except Exception as e:
        st.error(f"Error: {e}")
