# ⚡ Agentic AI Intake — Smart Lease Verification Pipeline

Agentic AI Intake is a multimodal document-processing system built to simulate how an AI agent could handle lease submissions for utilities, housing, or legal onboarding — from parsing to reasoning to user notification.

> ✅ Upload a lease  
> 🤖 AI reviews it page-by-page  
> 🖋 Detects missing signatures and lease dates  
> 📧 Notifies the customer (email, SMS, or callback)  
> 🧠 Uses GPT-4o + GPT-4o Vision to reason across text and images

---

## 🧠 Why This Exists

Most onboarding systems today are rule-based and fragile.

This project is a working prototype of an **agentic automation pipeline** that:
- Combines LLM summarization and function-calling
- Validates leases intelligently
- Escalates to GPT-4o Vision when needed (for signature field detection)
- Notifies humans based on context and preference

This was built with **real-world business use cases in mind** — like PECO (utility onboarding), property management, healthcare intake, or enterprise workflows.

---

## 🔍 Key Features

- ✅ Streamlit UI (submit + track document status)
- 📄 PDF-to-text cleaning and chunking
- 🧠 GPT-4o reasoning with function-calling
- 🖼️ GPT-4o Vision signature page detection
- 📬 Notification engine (email, SMS via Twilio, call-back queue)
- 📊 Business & engineering dashboards
- 🧾 Per-chunk summary traces + vision flags
- 📁 All logs and traces timestamped for inspection

---

## 🏗️ Architecture Overview

flowchart TD
  A[User Uploads PDF] --> B[Clean + Chunk Text]
  B --> C[GPT-4o Summary w/ Function Calls]
  C --> D{Signature/Dates Valid?}
  D -- No --> E[Trigger GPT-4o Vision on Flagged Pages]
  D -- Yes --> F[Notify User (Email/SMS/Call)]
  E --> F
  F --> G[Log + Update Dashboard]
