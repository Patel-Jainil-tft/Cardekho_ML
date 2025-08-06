import json
from agents import Agent, Runner
import logging
from mod.models import QueryRequest


formatting_instructions = """
You are a helpful assistant who reads raw JSON responses from the MCP system and explains the information in a natural, human way—like you're speaking to someone in a conversation.
Your responses should be clear, friendly, and easy to understand, without sounding robotic or technical. Avoid using code, field names, or formatting. Just provide a simple, polite explanation that feels like it's coming from a real person.
Only output the final human-friendly message—no code, no markdown, no JSON.
should be clear, concise, and to the point.
Example:

Input JSON:
{
  "uan_number": "123456789012",
  "status": "active",
  "name": "Rahul Sharma"
}

Expected Output:
"Your UAN number is 123456789012
"""
response_formatter_agent = Agent(
    name="ResponseFormatterAgent",
    instructions=formatting_instructions,
    model="gpt-4o-mini"
)
async def format_mcp_response(user_query: str, raw_response: dict) -> str:
    try:
        input_str = (
            f"User Query:\n{user_query}\n\n"
            f"Raw MCP response:\n{json.dumps(raw_response, indent=2)}"
        )
        result = await Runner.run(response_formatter_agent, input_str)
        return result.final_output.strip()
    except Exception:
        logging.exception("Failed to format MCP response.")
        return "I'm sorry, I could not summarize the response."