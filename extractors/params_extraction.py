import os
import logging
from dotenv import load_dotenv
from agents import Agent, Runner

load_dotenv()
api_key = os.environ["OPENAI_API_KEY"]

instructions = (
    "You are the HRMasterAgent for a conversational HR automation service. "
    "If the query contains a date (explicit or relative, e.g., 'today', 'last month', 'July 20, 2025'), extract it into a field called 'appliedDate' and standardize to DD-MM-YYYY format if possible. "
    "For the 'updateuserprofile' action, extract the following attributes from the user query and use exactly these names in the intent data: "
    "'updated_email_id', 'updated_mobile_number', 'salary_account_number', 'IFSC_code', 'marriage_status_to'. "
    "only extract the data field that exists in the user query, do not add any extra data to the data field and even don't add flied name if is does not exist in the user query."
    "Respond ONLY with a flat JSON object: {\"extracted_result\":{...}} "
    "Do not output any explanation, code block, or markdown, just the JSON."
)

hr_agent = Agent(
    name="HRMasterAgent",
    instructions=instructions,
    model="gpt-4o-mini"
)
async def extract_parameters(user_input):
    user_input = f"User message: \"{user_input}\""
    try:
        result = await Runner.run(hr_agent, user_input)
        import json
        intent_data = json.loads(result.final_output)
        logging.info(f"Extracted intent data: {intent_data}")
        return intent_data
    except Exception:
        logging.exception("Failed to extract parameters.")
        return {}
