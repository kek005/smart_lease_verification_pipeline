import streamlit as st
import json
import pandas as pd

st.set_page_config(page_title="📊 Business Dashboard", layout="wide")
st.title("📩 Processed Submissions")

try:
    with open("submission_log.json", "r") as f:
        logs = [json.loads(line) for line in f.readlines()]
except FileNotFoundError:
    logs = []

if logs:
    df = pd.DataFrame(logs)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    with st.expander("🔍 Filters", expanded=True):
        method = st.multiselect("Contact Method", df["method"].unique(), default=list(df["method"].unique()))
        df = df[df["method"].isin(method)]

    st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)
else:
    st.info("No submissions found yet.")