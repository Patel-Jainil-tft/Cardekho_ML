import os
from dotenv import load_dotenv
from agents import Agent, Runner

load_dotenv()
api_key = os.environ["OPENAI_API_KEY"]

instructions = (
    "You are the HRMasterAgent for a conversational HR automation service. "
    "Given any natural language user query, infer the correct HR system 'app' to use (e.g., darwinbox, careline), the type of action requested, and extract all useful data fields as a flat dictionary. "
    "Respond ONLY with a flat JSON object: {\"app\":..., \"action\":..., \"category\":..., \"data\":{...}} "
    "If the user query is only about updating marriage status, set app to 'careline'; otherwise use 'darwinbox'. "
    "Do not output any explanation, code block, or markdown, just the JSON."
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
    return intent_data
