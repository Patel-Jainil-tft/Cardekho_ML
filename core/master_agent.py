import os
import logging
from mod.models import QueryRequest, AgentResponse, Intent
from orchestration import extract_intent_and_slots
from custom_agents.darwinbox_agent import DarwinBoxAgent
from custom_agents.careline_agent import CarelineAgent
from integration.mcp_client import MCPServerClient

logging.basicConfig(level=logging.INFO)

class MasterAgent:
    def __init__(self):
        self.agents = {
            "darwinbox": DarwinBoxAgent(),
            "careline": CarelineAgent(),
        }
        base_url = os.getenv("MCP_SERVER_URL", "http://localhost:3001/mcp")
        self.mcp_client = MCPServerClient(base_url=base_url)
        tools_resp = self.mcp_client.fetch_tools()
        self.mcp_tools_list = tools_resp.get("result", {}).get("tools", [])
        logging.info(f"Available MCP Tools: {[t['name'] for t in self.mcp_tools_list]}")

    async def route_request(self, req: QueryRequest):
        intent_dict = await extract_intent_and_slots(req)
        intent_dict["data"]["userId"] = req.userId
        intent = Intent(**intent_dict)
        action_key = intent.action.replace("-", "_").replace(" ", "_").lower()

        matched_tool = None
        for tool in self.mcp_tools_list:
            tool_name = tool.get("name", tool).lower() if isinstance(tool, dict) else str(tool).lower()
            if tool_name == action_key:
                matched_tool = tool.get("name", tool)
                break

        if matched_tool:
            mcp_payload = {"userId": req.userId}
            if matched_tool.lower() == "viewreimbursementstatus":
                date_val = intent.data.get("appliedDate")
                if not date_val:
                    return AgentResponse(
                        success=False,
                        message="Please provide the date for which you want to check your reimbursement status.",
                        missing="appliedDate"
                    ), "mcp"
                mcp_payload["appliedDate"] = date_val

            mcp_result = self.mcp_client.call_action(matched_tool, mcp_payload)
            logging.info(f"MCP tool result: {mcp_result}")
            return AgentResponse(success=True, message="MCP tool executed", data=mcp_result), "mcp"

        agent_name = (intent.app or "").lower()
        if agent_name in self.agents:
            agent_resp = await self.agents[agent_name].handle(intent)
            return agent_resp, agent_name

        return AgentResponse(
            success=False,
            message="No matching agent found."
        ), agent_name