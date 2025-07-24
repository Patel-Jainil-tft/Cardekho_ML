
from mod.models import Intent, AgentResponse
from agents import Agent, Runner
from integration.mcp_client import MCPServerClient
from custom_agents.response_formatter import format_mcp_response 

# 1. Define your available tools
TOOL_LIST = [
    "updatePersonalDetails",
    "viewUAN",
    "viewListOfReportees"  # Add/modify as needed
]

# 2. Define the prompt for the OpenAI Agent
instructions = (
    "You are the DarwinBox Tool Selector agent for HR workflows."
    " Given an HR intent, extracted action, and parameters, "
    "choose ONLY the correct DarwinBox MCP tool name from the supported list for this request."
    " Respond ONLY with the tool name as a plain string—no explanation, JSON, or markdown.\n"
    "Supported tools:\n"
)
for tool in TOOL_LIST:
    instructions += f"- {tool}\n"

darwinbox_tool_agent = Agent(
    name="DarwinBoxToolAgent",
    instructions=instructions,
    model="gpt-4o-mini"
)

class DarwinBoxAgent:
    def __init__(self):
        self.mcp_client = MCPServerClient(base_url="http://localhost:3001/mcp")
        
        # Fetch tools response and extract proper tools list
        resp = self.mcp_client.fetch_tools()
        self.mcp_tools_list = resp.get("result", {}).get("tools", [])
        
        print("Fetched MCP tools:", self.mcp_tools_list)
        print("Available MCP Tool Names:",
              [tool['name'] for tool in self.mcp_tools_list])

        tool_names = [tool["name"] for tool in self.mcp_tools_list]
        instructions = (
            "You are the DarwinBox Tool Selector agent for HR workflows."
            " Given an HR intent, extracted action, and parameters, "
            "choose ONLY the correct DarwinBox MCP tool name from the supported list for this request."
            " Respond ONLY with the tool name as a plain string—no explanation, JSON, or markdown.\n"
            "Supported tools:\n"
        )
        for tool in tool_names:
            instructions += f"- {tool}\n"
        
        self.tool_agent = Agent(
            name="DarwinBoxToolAgent",
            instructions=instructions,
            model="gpt-4o-mini"
        )

    async def handle(self, intent: Intent) -> AgentResponse:
        user_prompt = (
            f"HR action: {intent.action}\n"
            f"Extracted fields: {intent.data}\n"
            "Which DarwinBox MCP tool from the supported list is the best match?"
        )
        result = await Runner.run(self.tool_agent, user_prompt)
        tool_name = result.final_output.strip().strip('"').strip("'")

        user_id = (
            intent.data.get("userId")
            or intent.data.get("userid")
            or intent.data.get("id")
        )
        print(f"Selected tool: {tool_name} for user ID: {user_id}")

        # Prepare MCP payload
        mcp_payload = {"userId": user_id}

        print(f"Selected tool: {tool_name} with payload: {mcp_payload}")

        # Call MCP server with the chosen tool
        mcp_result = self.mcp_client.call_action(tool_name, mcp_payload)
        human_message = await format_mcp_response(mcp_result)

        return AgentResponse(
            success=True,
            message=human_message,
            tool=tool_name,
            data=mcp_result
        )

