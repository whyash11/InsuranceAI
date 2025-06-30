🤖 Smart Insurance Agent
Smart Insurance Agent is a streamlined, AI-powered web application built with Streamlit and LangChain, offering users a simplified and intelligent interface to explore key vehicle insurance functionalities. With integrated tools for calculating premiums, checking claim statuses, estimating risk, and more — this solution simulates how conversational AI can assist users in real-time insurance decisions.

🚀 Features
Premium Calculator
Get a detailed breakdown of insurance premiums based on age, vehicle type, coverage, driving history, and location-specific risk using the Mappls API.

Claims Lookup
Retrieve claim status and resolution details with a simple claim ID.

Quote + Advice
Receive premium estimates and personalized AI-powered recommendations to help make smarter insurance coverage decisions.

Policy Renewal
Track your policy expiry timeline and get timely renewal suggestions based on urgency.

Claim Probability Estimator
Understand the estimated probability of an insurance claim based on your risk profile.

🌐 Real-Time API Integration
This project connects with Mappls (formerly MapMyIndia) to automatically determine the user's location and adjust premium calculations based on risk-prone areas like Delhi, Mumbai, and Gurgaon.

🗺️ Location detection is automatic — no input required by the user.

🛠️ Tech Stack
Python

Frontend/UI: Streamlit

AI Backend: LangChain + OpenAI ChatGPT

APIs Used:

OpenAI GPT API

Mappls API (GeoCode + IP Location)

🧪 Installation
1. Clone the repository:
bash
Copy
Edit
git clone https://github.com/yourusername/smart-insurance-agent.git
cd smart-insurance-agent
2. Set up environment:
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
3. Create a .env file and add:
ini
Copy
Edit
OPENAI_API_KEY=your_openai_key_here
MAPMYINDIA_API_KEY=your_mappls_key_here
4. Run the app:
bash
Copy
Edit
streamlit run app.py
📸 UI Preview
Home Interface	Premium Calculator (with location)	Claim Lookup

👥 Built By
🔧 Nitin Kadyan
– Developed the Policy Renewal Tool and Claim Probability Estimator Tool, enabling timely reminders and risk analysis.

🔧 Shashwat Dash
– Engineered the core logic and BaseTool setups for the Premium Calculator, Claims Lookup, and Quote + Advice tools, forming the functional core of the assistant.

🔧 Yash Kapoor
– Built the complete Streamlit UI, designed the user journey, and integrated the Mappls API to introduce location-based risk into the Premium Calculator.

📄 License
This project is licensed under the MIT License.
