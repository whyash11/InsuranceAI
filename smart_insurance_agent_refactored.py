import os
import json
import requests
from typing import ClassVar
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.tools import BaseTool

openai_key = "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"
mapmyindia_key = "bbd5e7f6ea983f19d26288ca5d0ac71b"

assert openai_key is not None, "Missing OpenAI API key. Add it to your .env file."

llm = ChatOpenAI(temperature=0.2, openai_api_key=openai_key)

# === Tool 1: Premium Calculator ===
class PremiumCalculatorTool(BaseTool):
    name: ClassVar[str] = "premium_calculator"
    description: ClassVar[str] = (
        "Calculate insurance premium with detailed breakdown. Input JSON: {age, vehicle_type, coverage_amount, driving_history (clean/minor/major)}."
    )

    def _run(self, input_str: str) -> str:
        try:
            data = json.loads(input_str)
            age = int(data["age"])
            vehicle_type = data["vehicle_type"].lower()
            coverage_amount = float(data["coverage_amount"])
            driving_history = data.get("driving_history", "clean").lower()

            # Step 1: Get IP-based location
            location_city = ""
            try:
                ip_resp = requests.get("https://ipapi.co/json/")
                if ip_resp.ok:
                    loc_data = ip_resp.json()
                    lat = loc_data.get("latitude")
                    lon = loc_data.get("longitude")

                    # Step 2: Reverse geocode using Mappls
                    if lat and lon and mapmyindia_key:
                        reverse_url = f"https://apis.mappls.com/advancedmaps/v1/{mapmyindia_key}/rev_geocode"
                        resp = requests.get(reverse_url, params={"lat": lat, "lng": lon})
                        if resp.ok:
                            results = resp.json().get("results", [])
                            if results:
                                location_city = results[0].get("city", "")
            except Exception:
                location_city = ""

            # Step 3: Adjust risk based on city
            risk_factor = 1.0
            high_risk_cities = ["Delhi", "Mumbai", "Gurgaon","Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad", "Jaipur","New Delhi", "Noida", "Ghaziabad", "Faridabad", "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal", "Coimbatore"]
            if location_city in high_risk_cities:
                risk_factor = 1.2

            # Step 4: Premium logic
            base = 500
            age_factor = 1 + max(age - 25, 0) * 0.015
            type_factor = {"sedan": 1, "suv": 1.2, "truck": 1.4}.get(vehicle_type, 1.1)
            history_factor = {"clean": 1, "minor": 1.15, "major": 1.3}.get(driving_history, 1.1)

            premium = base * age_factor * type_factor * history_factor * risk_factor * coverage_amount / 10000
            breakdown = {
                "base_premium": base,
                "age_factor": age_factor,
                "vehicle_type_factor": type_factor,
                "driving_history_factor": history_factor,
                "location_factor": risk_factor,
                "location_city": location_city,
                "coverage_amount": coverage_amount,
                "final_premium": round(premium, 2)
            }
            return json.dumps(breakdown, indent=2)

        except Exception as e:
            return f"Error in PremiumCalculatorTool: {str(e)}"

    def _arun(self, input_str: str):
        raise NotImplementedError()

# === Tool 2: Claims Lookup ===
class ClaimsLookupTool(BaseTool):
    name: ClassVar[str] = "claims_lookup"
    description: ClassVar[str] = "Lookup insurance claim status by claim ID and provide estimated resolution time."
    mock_db: ClassVar[dict] = {
        "C123": {"status": "Approved", "resolution": "Payment processed on 2024-05-15"},
        "C124": {"status": "Processing", "resolution": "Expected by 2024-07-01"},
        "C125": {"status": "Rejected", "resolution": "Rejected due to policy lapse"},
    }

    def _run(self, claim_id: str) -> str:
        record = self.mock_db.get(claim_id, None)
        if record:
            return f"Claim ID {claim_id}:\nStatus: {record['status']}\nResolution Info: {record['resolution']}"
        return f"Claim ID {claim_id} not found. Please check your ID or contact support."

    def _arun(self, claim_id: str):
        raise NotImplementedError()

# === Tool 3: Quote + Advice ===
quote_prompt = PromptTemplate(
    input_variables=["age", "vehicle_type", "coverage_amount"],
    template=(
        "Estimate a premium based on the following: "
        "Age={age}, Vehicle={vehicle_type}, Coverage={coverage_amount}. "
        "Include reasoning for risk factors."
    )
)

advice_prompt = PromptTemplate(
    input_variables=["quote"],
    template="You got a quote of ${quote}. Is this reasonable for the user? Explain and suggest whether they should reduce or increase coverage."
)

def run_quote_advice(data: dict):
    quote_chain = quote_prompt | llm
    quote = quote_chain.invoke(data)
    advice_chain = advice_prompt | llm
    advice = advice_chain.invoke({"quote": quote.content})
    return {
        "quote": quote.content.strip(),
        "advice": advice.content.strip()
    }

class QuoteAdviceTool(BaseTool):
    name: ClassVar[str] = "quote_advice"
    description: ClassVar[str] = "Get detailed premium quote and advice. Input JSON: {age, vehicle_type, coverage_amount}"

    def _run(self, input_str: str) -> str:
        try:
            data = json.loads(input_str)
            result = run_quote_advice(data)
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error in QuoteAdviceTool: {str(e)}"

    def _arun(self, input_str: str):
        raise NotImplementedError()

# === Tool 4: Policy Renewal Reminder ===
class PolicyRenewalTool(BaseTool):
    name: ClassVar[str] = "policy_renewal"
    description: ClassVar[str] = "Check upcoming policy renewal dates and provide renewal suggestions. Input JSON: {policy_id, expiry_date, current_premium}" 

    def _run(self, input_str: str) -> str:
        from datetime import datetime
        try:
            data = json.loads(input_str)
            expiry = datetime.strptime(data["expiry_date"], "%Y-%m-%d")
            today = datetime.today()
            days_left = (expiry - today).days
            renewal_msg = ""
            if days_left > 30:
                renewal_msg = "Your policy is active. Early renewal can offer discounts."
            elif 0 < days_left <= 30:
                renewal_msg = "Renew now to avoid policy lapse. You’re eligible for fast-track renewal."
            elif days_left <= 0:
                renewal_msg = "Policy expired! Renew immediately to maintain coverage."
            return json.dumps({
                "policy_id": data["policy_id"],
                "days_until_expiry": days_left,
                "current_premium": data["current_premium"],
                "recommendation": renewal_msg
            }, indent=2)
        except Exception as e:
            return f"Error in PolicyRenewalTool: {str(e)}"

    def _arun(self, input_str: str):
        raise NotImplementedError()

# === Tool 5: Claim Probability Estimator ===
class ClaimProbabilityTool(BaseTool):
    name: ClassVar[str] = "claim_probability"
    description: ClassVar[str] = "Estimate probability of a claim in the next year based on risk profile. Input JSON: {age, vehicle_type, driving_history, annual_mileage}" 

    def _run(self, input_str: str) -> str:
        try:
            data = json.loads(input_str)
            score = 0

            if data["age"] < 25:
                score += 2
            elif data["age"] > 60:
                score += 1

            vehicle_risk = {"sedan": 1, "suv": 2, "truck": 3}
            score += vehicle_risk.get(data["vehicle_type"].lower(), 1)

            history_risk = {"clean": 0, "minor": 2, "major": 3}
            score += history_risk.get(data["driving_history"].lower(), 1)

            if data["annual_mileage"] > 15000:
                score += 2
            elif data["annual_mileage"] > 10000:
                score += 1

            if score <= 3:
                risk = "Low (<15%)"
            elif score <= 6:
                risk = "Medium (15-30%)"
            else:
                risk = "High (>30%)"

            return json.dumps({
                "risk_score": score,
                "estimated_claim_probability": risk,
                "insights": "Reduce mileage and maintain clean driving to lower risk."
            }, indent=2)
        except Exception as e:
            return f"Error in ClaimProbabilityTool: {str(e)}"

    def _arun(self, input_str: str):
        raise NotImplementedError()

# === Assemble Tools ===
tools = [
    Tool.from_function(PremiumCalculatorTool()._run, name="premium_calculator", description=PremiumCalculatorTool.description),
    Tool.from_function(ClaimsLookupTool()._run, name="claims_lookup", description=ClaimsLookupTool.description),
    Tool.from_function(QuoteAdviceTool()._run, name="quote_advice", description=QuoteAdviceTool.description),
    Tool.from_function(PolicyRenewalTool()._run, name="policy_renewal", description=PolicyRenewalTool.description),
    Tool.from_function(ClaimProbabilityTool()._run, name="claim_probability", description=ClaimProbabilityTool.description),
]

# === Memory & Agent ===
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)
