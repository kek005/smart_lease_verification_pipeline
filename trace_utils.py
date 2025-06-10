import json
import glob
import os

def suggest_vision_pages(trace_file_path: str):
    try:
        with open(trace_file_path, "r") as f:
            trace_data = json.load(f)
    except Exception as e:
        print(f"[❌] Failed to read {trace_file_path}: {e}")
        return []

    pages_to_flag = []
    for entry in trace_data:
        summary = entry.get("summary", "").lower()
        if "signature" in summary or "signed" in summary or "missing signature" in summary:
            pages_to_flag.append(entry["page"])

    return sorted(set(pages_to_flag))

def get_latest_trace_file():
    trace_files = sorted(glob.glob("trace_summary_*.json"), reverse=True)
    return trace_files[0] if trace_files else None