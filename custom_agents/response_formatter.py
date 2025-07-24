from agents import Agent, Runner

# Define instructions to tell the LLM how to humanize MCP output.
formatting_instructions = """
You are a helpful assistant that takes a raw JSON response from the MCP HR system and
summarizes it into a clear, concise, human-readable response suitable for end users.
Only output the summary text—no code, no markdown, no JSON.

Example input: 
{
  "result": {
    "content": [
      {"type": "text", "text": "100621693455"}
    ]
  }
}

Example output:
"The employee's UAN number is 100621693455."
"""

response_formatter_agent = Agent(
    name="ResponseFormatterAgent",
    instructions=formatting_instructions,
    model="gpt-4o-mini"  # or your preferred model
)

async def format_mcp_response(raw_response: dict) -> str:
    import json
    # Provide raw JSON as string input to the agent prompt
    input_str = f"Raw MCP response:\n{json.dumps(raw_response, indent=2)}"
    result = await Runner.run(response_formatter_agent, input_str)
    return result.final_output.strip()