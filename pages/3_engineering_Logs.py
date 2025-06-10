import streamlit as st
import json
import pandas as pd

st.set_page_config(page_title="🛠 Engineering Logs", layout="wide")
st.title("🧪 Extraction Errors")

try:
    with open("error_log.json", "r") as f:
        logs = [json.loads(line) for line in f.readlines()]
except FileNotFoundError:
    logs = []

if logs:
    df = pd.DataFrame(logs)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)
else:
    st.info("No errors have been logged yet.")