from mod.models import QueryRequest, AgentResponse, Intent

from orchestration import extract_intent_and_slots
from custom_agents.darwinbox_agent import DarwinBoxAgent
from custom_agents.careline_agent import CarelineAgent
from integration.mcp_client import MCPServerClient

class MasterAgent:
    def __init__(self):
        self.agents = {
            "darwinbox": DarwinBoxAgent(),
            "careline": CarelineAgent(),
        }
        self.mcp_client = MCPServerClient(base_url="http://localhost:3001/mcp")
        # Fetch the list of available tools at init or cache it if performance is a concern
        self.mcp_tools_list = self.mcp_client.fetch_tools()
        print("Available MCP Tools:", self.mcp_tools_list)


    async def route_request(self, req: QueryRequest):
        intent_dict = await extract_intent_and_slots(req)
        intent_dict["data"]["userId"] = req.userId
        intent = Intent(**intent_dict)
        print(f"Extracted intent: {intent}")

        # Get the action key (normalization as in your original code)
        action_key = intent.action.replace("-", "_").replace(" ", "_").lower()

        # Find the best matching tool by name (can extend to fuzzy/semantic match)
        matched_tool = None
        for tool in self.mcp_tools_list:
            if isinstance(tool, dict) and "name" in tool:
                tool_name = tool["name"]
            else:
                tool_name = tool
            if tool_name.lower() == action_key:
                matched_tool = tool_name
                break


        if matched_tool:
            data = {"userId": req.userId}
            mcp_result = self.mcp_client.call_action(matched_tool, data)
            print(f"MCP tool result: {mcp_result}")
            return AgentResponse(success=True, message="MCP tool executed", data=mcp_result), "mcp"

        agent_name = (intent.app or "").lower()
        if agent_name in self.agents:
            agent_resp = await self.agents[agent_name].handle(intent)
            return agent_resp, agent_name
        else:
            return AgentResponse(success=False, message="No matching agent found."), agent_name
