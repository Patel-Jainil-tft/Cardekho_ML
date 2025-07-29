import json
from agents import Agent, Runner

formatting_instructions = """
You are a helpful assistant that takes a raw JSON response from the MCP system and
summarizes it into a clear, concise, human-readable response suitable for end users.
Only output the summary text—no code, no markdown, no JSON.
"""

response_formatter_agent = Agent(
    name="ResponseFormatterAgent",
    instructions=formatting_instructions,
    model="gpt-4o-mini"
)

async def format_mcp_response(raw_response: dict) -> str:
    """
    Format raw MCP JSON response into human-readable summary.
    """
    input_str = f"Raw MCP response:\n{json.dumps(raw_response, indent=2)}"
    result = await Runner.run(response_formatter_agent, input_str)
    return result.final_output.strip()
