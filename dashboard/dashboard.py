# dashboard/dashboard.py
# ─────────────────────────────────────────────
# Streamlit Dashboard
# Run: streamlit run dashboard/dashboard.py
# ─────────────────────────────────────────────

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Group Email Summarizer",
    page_icon="📧",
    layout="wide",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .header {
        background: linear-gradient(135deg, #1a73e8, #0d47a1);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .metric-box {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e9ecef;
    }
</style>
<div class="header">
    <h1 style="margin:0">📧 Group Email Summarizer Dashboard</h1>
    <p style="margin:0.3rem 0 0; opacity:0.85;">
        Powered by Gmail API · Google Gemini AI · Python · Streamlit
    </p>
</div>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(__file__), "../data/email_summary.csv")

if not os.path.exists(CSV_PATH):
    st.warning("⚠️ No data found. Run the pipeline first:")
    st.code("python app.py")
    st.stop()

df = pd.read_csv(CSV_PATH)

if df.empty:
    st.warning("CSV is empty. Run `python app.py` to fetch and process emails.")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Filters")

    priority_options = ["High", "Medium", "Low"]
    selected_priority = st.multiselect(
        "Filter by Priority",
        options=priority_options,
        default=priority_options,
    )

    search_term = st.text_input("🔎 Search threads", placeholder="keyword…")

    st.divider()
    st.caption(f"Total threads: **{len(df)}**")

    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ── Apply Filters ─────────────────────────────────────────────────────────────
filtered = df[df["Priority"].isin(selected_priority)]

if search_term:
    mask = (
        filtered["Email Thread"].str.contains(search_term, case=False, na=False) |
        filtered["Key Topic"].str.contains(search_term, case=False, na=False) |
        filtered["Action Items"].str.contains(search_term, case=False, na=False)
    )
    filtered = filtered[mask]

# ── KPI Row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("📧 Total Threads",      len(df))
k2.metric("🔴 High Priority",      len(df[df["Priority"] == "High"]))
k3.metric("🟡 Medium Priority",    len(df[df["Priority"] == "Medium"]))
k4.metric("🟢 Low Priority",       len(df[df["Priority"] == "Low"]))
k5.metric("✅ With Action Items",  len(df[df["Action Items"] != "None"]))

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋 Summary Table", "🧵 Thread Details", "📊 Insights"])

# ── Tab 1: Summary Table ──────────────────────────────────────────────────────
with tab1:
    st.subheader(f"Email Thread Summary  ({len(filtered)} threads)")

    display_cols = [
        "Email Thread", "Key Topic", "Action Items",
        "Owner", "Follow-up Date", "Priority", "Tags"
    ]
    available = [c for c in display_cols if c in filtered.columns]

    def color_priority(val):
        return {
            "High":   "background-color:#fee2e2; color:#dc2626",
            "Medium": "background-color:#fef9c3; color:#b45309",
            "Low":    "background-color:#dcfce7; color:#15803d",
        }.get(val, "")

    styled = filtered[available].style.applymap(color_priority, subset=["Priority"])
    st.dataframe(styled, use_container_width=True, height=450)

    csv_export = filtered.to_csv(index=False)
    st.download_button("⬇️ Export to CSV", csv_export, "email_summary.csv", "text/csv")

# ── Tab 2: Thread Details ─────────────────────────────────────────────────────
with tab2:
    st.subheader("Individual Thread Analysis")

    for _, row in filtered.iterrows():
        icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(row.get("Priority", ""), "⚪")

        with st.expander(f"{icon}  {row['Email Thread']}  —  {row.get('Last Date', '')}"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**🏷️ Key Topic:** {row.get('Key Topic', '—')}")
                st.markdown("**📝 Summary:**")
                st.info(row.get("Summary", "—"))
                st.markdown(f"**✅ Action Items:** {row.get('Action Items', 'None')}")

            with col2:
                st.markdown(f"**👤 Owner:** {row.get('Owner', '—')}")
                st.markdown(f"**👥 Participants:** {row.get('Participants', '—')}")
                st.markdown(f"**📅 Follow-up:** {row.get('Follow-up Date', '—')}")
                st.markdown(f"**🚦 Priority:** {row.get('Priority', '—')}")
                st.markdown(f"**🔖 Tags:** {row.get('Tags', '—')}")

# ── Tab 3: Insights ───────────────────────────────────────────────────────────
with tab3:
    st.subheader("📊 Email Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🚦 Priority Distribution**")
        priority_counts = df["Priority"].value_counts()
        st.bar_chart(priority_counts)

    with col2:
        st.markdown("**👤 Action Items by Owner**")
        owner_counts = (
            df[df["Action Items"] != "None"]["Owner"]
            .value_counts()
            .head(8)
        )
        if not owner_counts.empty:
            st.bar_chart(owner_counts)
        else:
            st.info("No action items found.")

    st.markdown("**🔖 Most Discussed Topics (Tags)**")
    all_tags = []
    for tags in df["Tags"].dropna():
        all_tags.extend([t.strip() for t in str(tags).split(",") if t.strip()])
    if all_tags:
        tag_counts = pd.Series(all_tags).value_counts().head(10)
        st.bar_chart(tag_counts)
    else:
        st.info("No tags found.")

    st.markdown("**📅 Threads with Pending Follow-ups**")
    pending = df[
        df["Follow-up Date"].notna() &
        (df["Follow-up Date"] != "—") &
        (df["Follow-up Date"] != "")
    ][["Email Thread", "Key Topic", "Owner", "Follow-up Date"]]

    if not pending.empty:
        st.dataframe(pending, use_container_width=True)
    else:
        st.info("No follow-up dates found.")