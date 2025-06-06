import streamlit as st
from pdf_utils import extract_text_from_pdf
from agent_core import run_agent
from email_utils import send_email
from sms_utils import send_sms

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

# === Step 2: Validate Inputs ===
if not uploaded_file:
    st.warning("Please upload a valid document to continue.")

elif not user_email and not user_phone:
    st.warning("Please provide at least one way to reach you (email or SMS).")

# === Step 3: Run Agent ===
elif st.button("🚀 Verify Document"):
    with st.spinner("🔍 Processing your submission..."):
        text = extract_text_from_pdf(uploaded_file)

        if not text:
            st.error("❌ Could not extract text from the document.")
        else:
            response = run_agent(ticket_id, text)
            st.success("✅ Document processed by AI.")

            st.markdown("### 🤖 AI Response:")
            st.write(response)

            # === Step 4: Email Notification ===
            if user_email:
                email_sent = send_email(user_email, "Your Lease Review Result", response)
                if email_sent:
                    st.success("📧 Email sent to user.")
                else:
                    st.warning("⚠️ Failed to send email.")

            # === Step 5: (Optional) Queue Callbacks ===
            if contact_method == "Call Me":
                import json
                callback_data = {
                    "ticket_id": ticket_id,
                    "phone": user_phone,
                    "status": response
                }
                with open("followup_queue.json", "a") as f:
                    f.write(json.dumps(callback_data) + "\n")
                st.info("📞 Callback request added to human follow-up queue.")

            # SMS hook (optional)
            if contact_method == "SMS" and user_phone:
                # Clean and normalize the number
                cleaned_number = user_phone.strip().replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                
                if cleaned_number.startswith("+1"):
                    formatted_number = cleaned_number
                elif cleaned_number.startswith("1") and len(cleaned_number) == 11:
                    formatted_number = f"+{cleaned_number}"
                elif len(cleaned_number) == 10:
                    formatted_number = f"+1{cleaned_number}"
                else:
                    st.warning("⚠️ Please enter a valid 10-digit U.S. phone number.")
                    formatted_number = None

                if formatted_number:
                    sms_sent = send_sms(formatted_number, response)
                    if sms_sent:
                        st.success(f"📱 SMS sent to {formatted_number}.")
                    else:
                        st.warning("⚠️ Failed to send SMS.")