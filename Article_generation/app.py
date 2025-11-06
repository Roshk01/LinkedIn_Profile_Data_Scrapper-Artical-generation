# app_blog.py
import os
import io
import zipfile
import streamlit as st
import pandas as pd

from function import generate_articles

st.set_page_config(page_title="AI Blog (Gemini)", page_icon="📝", layout="wide")
st.title("📝 AI Blog Generator")

# Load Gemini API Key
if "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
else:
    st.error(" Missing GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# UI Instructions
st.write("Enter topics (one per line). Format:")
st.code("Title | brief/description (optional)")

# User input box
user_input = st.text_area(
    "Paste article topics:",
    height=240,
    placeholder=(
        "Python Decorators | intro + examples\n"
        "Async IO in Python\n"
        "Vector Database | basics + usage"
    )
)

length = st.number_input("Words per article", min_value=300, max_value=2000, value=800, step=50)
level = st.selectbox("Audience level", ["beginner", "intermediate", "advanced"], index=1)


# ============================
# GENERATE ARTICLES
# ============================
if st.button("Generate Articles"):
    if not user_input.strip():
        st.error(" Please enter topics.")
        st.stop()

    try:
        articles = generate_articles(
            user_input,
            limit=10,
            length=length,
            level=level
        )

        df = pd.DataFrame(articles)
        st.success(f" Generated {len(df)} articles.")

        # --------- Show summary table ----------
        st.dataframe(df[["title", "brief"]], use_container_width=True, height=420)

        # --------- CSV Download ----------
        st.download_button(
            "⬇️ Download CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="articles.csv",
            mime="text/csv",
        )

        # --------- ZIP of All Markdown ----------
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as z:
            for _, row in df.iterrows():
                filename = f"{row['title'].replace(' ', '_')}.md"
                z.writestr(filename, row["markdown"])

        st.download_button(
            "⬇️ Download All Articles (ZIP)",
            zip_buffer.getvalue(),
            file_name="articles_markdown.zip",
            mime="application/zip",
        )

        # --------- Show All Articles ----------
        st.markdown("## Full Articles")
        for i, row in df.iterrows():
            with st.expander(f"{i+1}. {row['title']}"):
                st.markdown(row["markdown"])

                # Individual MD download
                st.download_button(
                    "⬇️ Download This Article (Markdown)",
                    row["markdown"],
                    file_name=f"{row['title'].replace(' ', '_')}.md",
                    mime="text/markdown",
                )


    except Exception as e:
        st.error(f" Error: {e}")
