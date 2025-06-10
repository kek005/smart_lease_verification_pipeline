import streamlit as st
from pdf_utils import find_signature_page, extract_signature_image
from agent_core import run_agent
from email_utils import send_email
from sms_utils import send_sms
from vision_utils import check_signature_image
from submission_logger import log_submission
from error_logger import log_extraction_error
from trace_utils import suggest_vision_pages
import os
import json
import time

st.set_page_config(page_title="Agentic AI Intake", layout="wide")
st.title("⚡ Onboarding — Agentic AI Demo")

st.markdown("Submit your lease or ID. Our AI will validate it and notify you automatically.")

# === Step 1: Upload and Inputs ===
uploaded_file = st.file_uploader("📄 Upload your lease or ID (PDF only)", type=["pdf"])
ticket_id = st.text_input("🎫 Ticket Number (optional)")

st.subheader("📬 Contact Preferences")
col1, col2, col3 = st.columns(3)
user_email = col1.text_input("📧 Email Address")
user_phone = col2.text_input("📱 SMS Number (optional)")
contact_method = col3.selectbox("Preferred Follow-Up Method", ["Email", "SMS", "Call Me"])

# === Step 2: Always show the button ===
proceed = st.button("🚀 Verify Document")

if proceed:
    if not uploaded_file:
        st.warning("📄 Please upload a valid document to continue.")
    elif not user_email and not user_phone:
        st.warning("📬 Please provide at least one way to reach you (email or phone).")
    else:
        start_time = time.time()
        with st.spinner("🔍 Processing your submission..."):
            # Save uploaded file to disk
            uploaded_file_path = "uploaded_lease.pdf"
            with open(uploaded_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Run reasoning agent on the uploaded file path
            try:
                response, trace_file = run_agent(ticket_id, uploaded_file_path)
            except Exception as e:
                st.error("❌ GPT processing failed. Check logs.")
                log_extraction_error(
                    ticket_id=ticket_id,
                    filename=uploaded_file.name,
                    error_detail=str(e)
                )
                st.stop()

            elapsed_time = time.time() - start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)

            st.success(f"✅ Document processed in {minutes} min {seconds} sec.")

            st.success("✅ Document processed by AI.")
            st.markdown("### 🤖 AI Response:")
            st.write(response)
            if "lease begins" in response.lower() or "move-in" in response.lower():
                st.success("📅 Lease dates found in summary.")
            elif "dates not present but expected" in response.lower():
                st.error("⚠️ Lease start/end dates missing.")

            # === Step 3: Email Notification ===
            if user_email:
                email_sent = send_email(user_email, "Your Lease Review Result", response)
                if email_sent:
                    st.success("📧 Email sent to user.")
                else:
                    st.warning("⚠️ Failed to send email.")

            # === Step 4: Callback Queue ===
            if contact_method == "Call Me":
                callback_data = {
                    "ticket_id": ticket_id,
                    "phone": user_phone,
                    "status": response
                }
                with open("followup_queue.json", "a") as f:
                    f.write(json.dumps(callback_data) + "\n")
                st.info("📞 Callback request added to human follow-up queue.")

            # === Step 5: SMS Notification ===
            if contact_method == "SMS" and user_phone:
                cleaned = user_phone.strip().replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                if cleaned.startswith("+1"):
                    formatted = cleaned
                elif cleaned.startswith("1") and len(cleaned) == 11:
                    formatted = f"+{cleaned}"
                elif len(cleaned) == 10:
                    formatted = f"+1{cleaned}"
                else:
                    st.warning("⚠️ Please enter a valid 10-digit U.S. phone number.")
                    formatted = None

                if formatted:
                    sms_sent = send_sms(formatted, response)
                    if sms_sent:
                        st.success(f"📱 SMS sent to {formatted}.")
                    else:
                        st.warning("⚠️ Failed to send SMS.")

            # === Step 6: Log Submission ===
            log_submission(
                email=user_email,
                phone=user_phone,
                method=contact_method,
                ticket_id=ticket_id,
                result=response
            )

            # === Step 7: Flag Vision Pages ===
            flagged_pages = suggest_vision_pages(trace_file)
            if flagged_pages:
                st.markdown(f"🔍 Pages flagged for vision signature check: `{flagged_pages}`")

            # === Step 8: Vision Scan of Flagged Pages ===
            if flagged_pages:
                for page in flagged_pages:
                    image_path = extract_signature_image(uploaded_file_path, page)
                    if image_path and os.path.exists(image_path):
                        st.image(image_path, caption=f"Signature Page (Page {page})", use_container_width=True)

                        with st.spinner(f"🧠 Checking Page {page} for signature..."):
                            vision_result = check_signature_image(image_path)
                            st.markdown(f"### 🖋 Vision Result – Page {page}")
                            st.write(vision_result)
                    else:
                        st.warning(f"⚠️ Could not extract image for page {page}.")
            else:
                st.info("✅ No pages flagged for visual signature verification.")