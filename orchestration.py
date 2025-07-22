import os
from dotenv import load_dotenv
from agents import Agent, Runner

load_dotenv()
api_key = os.environ["OPENAI_API_KEY"]

# Generate your action schema listing for instruction string
from intent_classifier.action_resolver import ACTION_SCHEMA

instructions = (
    "You are the HRMasterAgent for a conversational HR automation service. "
    "Classify user queries into one of the supported actions below, and extract all required parameters for that action. "
    "Respond with only a JSON object: {\"app\":..., \"action\":..., \"category\":..., \"data\":{...}} per the schema. "
    "If the user only wants to update marriage status, set app to 'careline'; otherwise use 'darwinbox'.\n"
    "Do NOT output any explanation, header, footer, or extra text. Do NOT use markdown or code blocks. Output JSON only.\n"
)
for action, params in ACTION_SCHEMA.items():
    param_list = ", ".join(params) if params else "No parameters"
    instructions += f"- {action}: {param_list}\n"

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
    return intent_data