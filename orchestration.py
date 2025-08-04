import os
from dotenv import load_dotenv
from agents import Agent, Runner

load_dotenv()
api_key = os.environ["OPENAI_API_KEY"]

instructions = (
    "You are the HRMasterAgent for a conversational HR automation service.\n"
    "Your task is to:\n"
    "- Identify the correct HR system \"app\" to use from the supported list: [\"darwinbox\", \"careline\"].\n"
    "- For any query related to internal employee data (e.g., salary, UAN, profile updates, reimbursements, leave status, etc.), always use \"darwinbox\".\n"
    "- For external help, complaints, or general support queries (e.g., talk to HR, raise a concern, contact support), use \"careline\".\n"
    "\n"
    "Respond ONLY with a flat JSON object:\n"
    "{\"app\": ..., \"action\": ..., \"category\": ..., \"data\": {...}}\n"
    "\n"
    "Never wrap output in code blocks, markdown, or add extra text. Do not hallucinate or add extra fields to the \"data\" key — include only what is explicitly mentioned in the user input."

)


hr_agent = Agent(
    name="HRMasterAgent",
    instructions=instructions,
    model="gpt-4o-mini"
)

async def extract_intent_and_slots(query):
    user_input = f"User message: \"{query.message}\""
    result = await Runner.run(hr_agent, user_input)
    import json
    intent_data = json.loads(result.final_output)
    intent_data["user_input"] = query.message
    print(f"Extracted intent data: {intent_data}")
    return intent_data