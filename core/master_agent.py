from mod.models import QueryRequest, AgentResponse
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

    async def route_request(self, req: QueryRequest):
        intent = await extract_intent_and_slots(req)
        print(f"OpenAI Agent extracted: {intent}")
        # MCP tool routing (unchanged)
        mcp_tools = {
            "view_uan": "viewUAN",
            "view_list_of_reportees": "viewListOfReportees"
        }
        action_key = intent["action"].replace("-", "_").replace(" ", "_").lower()
        tool_endpoint = mcp_tools.get(action_key)
        if tool_endpoint:
            data = {"userId": req.userId}
            mcp_result = self.mcp_client.call_action(tool_endpoint, data)
            return AgentResponse(success=True, message="MCP tool executed", data=mcp_result), "mcp"
        agent_name = (intent["app"] or "").lower()
        if agent_name in self.agents:
            return self.agents[agent_name].handle(intent), agent_name
        else:
            return AgentResponse(success=False, message="No matching agent found."), agent_name
