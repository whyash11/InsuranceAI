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

# === Streamlit Page Setup ===
st.set_page_config(page_title="Smart Insurance Agent", page_icon="🤖", layout="centered")

# === Global Custom Styling ===
st.markdown("""
    <style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    font-family: 'Georgia', serif;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Impact', sans-serif !important;
    color: #000000 !important;
}

label, input, select, textarea, .stTextInput, .stNumberInput {
    color: #000000 !important;
    background-color: #FFFFFF !important;
}

.stSelectbox, .stTextInput, .stNumberInput, .stDateInput {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border-radius: 5px;
}

div[data-testid="stMarkdownContainer"] pre {
    background-color: #FEEFDD;
    color: #000000;
    padding: 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
}

button[kind="primary"] {
    background-color: #FF4000 !important;
    color: white !important;
    font-weight: bold;
}

.scroll-indicator {
    color: #FF4000;
    animation: bounce 2s infinite;
}

.hero {
    padding: 4rem 1rem;
    text-align: center;
    background-color: #ffffff;
}

.gradient-text {
    background: linear-gradient(to right, #FF4000, #000000);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>

""", unsafe_allow_html=True)

# === Hero Section ===
st.markdown("""
<div class="hero">
    <div class="avatar">
    </div>
    <h1 style="font-size: 3rem; margin-top: 1rem;">
        Meet Your <br>
        <span class="gradient-text">AI Insurance Agent</span>
    </h1>
    <p style="font-size: 1.1rem; color: #000000; margin-top: 1rem; max-width: 600px; margin-left: auto; margin-right: auto;">
        Get personalized insurance recommendations, instant quotes, and expert guidance 
        powered by artificial intelligence. Let us simplify your insurance journey.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="scroll-indicator">↓ Scroll to get started ↓</div>
""", unsafe_allow_html=True)

st.divider()

# === Functional UI ===
st.subheader("🛠️ Select a Service")

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

# Fetch detected city for Premium Calculator
user_city = None
if service == "Premium Calculator":
    try:
        ip_data = requests.get("https://ipinfo.io/json").json()
        loc = ip_data.get("loc")
        if loc:
            lat, lon = loc.split(",")
            reverse_geocode = requests.get("https://apis.mappls.com/advancedmaps/v1/{YOUR_MAPPLS_REST_KEY}/rev_geocode", params={"lat": lat, "lng": lon})
            if reverse_geocode.ok:
                place = reverse_geocode.json().get("results", [{}])[0].get("formatted_address")
                if place:
                    user_city = place
    except:
        pass

if service in ["Premium Calculator", "Quote + Advice", "Claim Probability Estimator"]:
    age = st.number_input("Enter your age", min_value=16, max_value=100, value=30)
    vehicle_type = st.selectbox("Select vehicle type", ["Sedan", "SUV", "Truck"])
    coverage_amount = st.number_input("Enter desired coverage amount", value=25000.0)
    driving_history = st.selectbox("Driving history", [
        "Clean (No previous claims)",
        "Minor (1-2 incident reports)",
        "Major (More than 2 incident reports)"
    ]).split("(")[0].strip().lower() if service != "Quote + Advice" else "clean"

    input_json = {
        "age": age,
        "vehicle_type": vehicle_type,
        "coverage_amount": coverage_amount,
        "driving_history": driving_history
    }

    if service == "Premium Calculator" and user_city:
        st.markdown(f"**📍 Detected Location:** {user_city}")
        input_json["location"] = user_city

    if service == "Claim Probability Estimator":
        annual_mileage = st.number_input("Annual mileage (in km)", min_value=1000, max_value=100000, value=12000)
        input_json = {
            "age": age,
            "vehicle_type": vehicle_type,
            "driving_history": driving_history,
            "annual_mileage": annual_mileage
        }

    input_str = json.dumps(input_json)
    user_query = f"{service} with {input_str}"

elif service == "Claims Lookup":
    claim_id = st.text_input("Enter your Claim ID (e.g., C123)")
    if claim_id:
        input_json = claim_id
        user_query = f"{service} for {claim_id}"

elif service == "Policy Renewal":
    policy_id = st.text_input("Enter your Policy ID")
    expiry_date = st.date_input("When does your policy expire?")
    current_premium = st.number_input("Current annual premium", min_value=1000.0, value=5000.0)
    input_json = json.dumps({
        "policy_id": policy_id,
        "expiry_date": str(expiry_date),
        "current_premium": current_premium
    })
    user_query = f"{service} for {policy_id}"

# === Submission and Result ===
if user_query and st.button("Submit"):
    try:
        if service == "Premium Calculator":
            tool = PremiumCalculatorTool()
            response = tool.run(json.dumps(input_json))
        elif service == "Claims Lookup":
            tool = ClaimsLookupTool()
            response = tool.run(input_json)
        elif service == "Quote + Advice":
            tool = QuoteAdviceTool()
            response = tool.run(json.dumps(input_json))
        elif service == "Policy Renewal":
            tool = PolicyRenewalTool()
            response = tool.run(input_json)
        elif service == "Claim Probability Estimator":
            tool = ClaimProbabilityTool()
            response = tool.run(json.dumps(input_json))
    except Exception as e:
        response = f"⚠️ Error: {e}"

    st.session_state.setdefault("history", []).append((user_query, response))

# === Chat History ===
if "history" in st.session_state:
    st.subheader("💬 Interaction History")
    for user_msg, bot_msg in reversed(st.session_state["history"]):
        st.markdown(f"<b>🧑 You:</b> {user_msg}", unsafe_allow_html=True)
        st.markdown(f"<b>🤖 Agent:</b> <pre>{bot_msg}</pre>", unsafe_allow_html=True)
