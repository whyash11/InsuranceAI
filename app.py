import streamlit as st
import json
import requests
from smart_insurance_agent_refactored import (
    PremiumCalculatorTool,
    ClaimsLookupTool,
    QuoteAdviceTool,
    PolicyRenewalTool,
    ClaimProbabilityTool
)

# === Page Setup ===
st.set_page_config(page_title="Smart Insurance Agent", page_icon="🤖", layout="centered")
st.title("🤖 Smart Insurance Agent")

# === Get Geolocation Automatically ===
lat, lon = None, None
try:
    geo_resp = requests.get("https://ipapi.co/json/")
    if geo_resp.ok:
        geo = geo_resp.json()
        lat, lon = geo.get("latitude"), geo.get("longitude")
except:
    pass

# === UI Logic ===
services = [
    "Premium Calculator",
    "Claims Lookup",
    "Quote + Advice",
    "Policy Renewal",
    "Claim Probability Estimator"
]

service = st.selectbox("Choose a service:", services)
response = None
user_query = None
input_json = None

if service in ["Premium Calculator", "Quote + Advice", "Claim Probability Estimator"]:
    age = st.number_input("Enter your age", min_value=16, max_value=100, value=30)
    vehicle_type = st.selectbox("Select vehicle type", ["Sedan", "SUV", "Truck"])
    coverage_amount = st.number_input("Enter desired coverage amount", value=25000.0)
    driving_history = st.selectbox("Driving history", [
        "Clean (No previous claims)",
        "Minor (1-2 incident reports)",
        "Major (More than 2 incident reports)"
    ]).split("(")[0].strip().lower()

    if service == "Premium Calculator":
        st.write(f"📍 Location detected: {lat}, {lon}")
        input_dict = {
            "age": age,
            "vehicle_type": vehicle_type,
            "coverage_amount": coverage_amount,
            "driving_history": driving_history,
            "lat": lat,
            "lon": lon
        }

    elif service == "Quote + Advice":
        input_dict = {
            "age": age,
            "vehicle_type": vehicle_type,
            "coverage_amount": coverage_amount
        }

    elif service == "Claim Probability Estimator":
        annual_mileage = st.number_input("Annual mileage (in km)", min_value=1000, max_value=100000, value=12000)
        input_dict = {
            "age": age,
            "vehicle_type": vehicle_type,
            "driving_history": driving_history,
            "annual_mileage": annual_mileage
        }

    input_json = json.dumps(input_dict)
    user_query = f"{service} with {input_json}"

elif service == "Claims Lookup":
    claim_id = st.text_input("Enter your Claim ID (e.g., C123)")
    if claim_id:
        input_json = claim_id
        user_query = f"{service} for {claim_id}"

elif service == "Policy Renewal":
    policy_id = st.text_input("Enter your Policy ID")
    expiry_date = st.date_input("When does your policy expire?")
    current_premium = st.number_input("Current annual premium", min_value=1000.0, value=5000.0)
    input_dict = {
        "policy_id": policy_id,
        "expiry_date": str(expiry_date),
        "current_premium": current_premium
    }
    input_json = json.dumps(input_dict)
    user_query = f"{service} for {policy_id}"

# === Run Tool ===
if user_query and st.button("Submit"):
    try:
        if service == "Premium Calculator":
            tool = PremiumCalculatorTool()
            response = tool.run(input_json)
        elif service == "Claims Lookup":
            tool = ClaimsLookupTool()
            response = tool.run(input_json)
        elif service == "Quote + Advice":
            tool = QuoteAdviceTool()
            response = tool.run(input_json)
        elif service == "Policy Renewal":
            tool = PolicyRenewalTool()
            response = tool.run(input_json)
        elif service == "Claim Probability Estimator":
            tool = ClaimProbabilityTool()
            response = tool.run(input_json)
    except Exception as e:
        response = f"⚠️ Error: {e}"

    st.session_state.setdefault("history", []).append((user_query, response))

# === Show Chat History ===
if "history" in st.session_state:
    st.subheader("💬 Interaction History")
    for user_msg, bot_msg in reversed(st.session_state["history"]):
        st.markdown(f"**🧑 You:** {user_msg}")

        st.markdown("**🤖 Agent:**")
        try:
            parsed = json.loads(bot_msg)
            if isinstance(parsed, dict):
                for key, value in parsed.items():
                    label = key.replace('_', ' ').title()
                    emoji = ""

                    # Emoji mapping (customize as needed)
                    if "premium" in key:
                        emoji = "💰"
                    elif "factor" in key:
                        emoji = "📊"
                    elif "risk" in key:
                        emoji = "⚠️"
                    elif "location" in key:
                        emoji = "📍"
                    elif "coverage" in key:
                        emoji = "🛡️"
                    elif "days" in key or "date" in key:
                        emoji = "📅"
                    elif "quote" in key:
                        emoji = "📈"
                    elif "advice" in key:
                        emoji = "🧠"
                    elif "status" in key:
                        emoji = "🔍"
                    elif "resolution" in key:
                        emoji = "✅"

                    st.write(f"{emoji} **{label}:** {value}")
            else:
                st.code(str(bot_msg), language="json")
        except Exception:
            st.warning("⚠️ Couldn't format the response. Showing raw output below.")
            st.code(str(bot_msg), language="json")

