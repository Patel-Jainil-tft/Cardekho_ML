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

    @staticmethod
    def _extract_user_id(req):
        # Prefer token->darwinbox->employee_no if present
        token = getattr(req, "token", None)
        if token and isinstance(token, dict):
            dbx = token.get("darwinbox")
            if dbx and isinstance(dbx, dict):
                emp_no = dbx.get("employee_no")
                if emp_no:
                    return emp_no
        return req.userId or ""

    async def route_request(self, req: QueryRequest):
        intent_dict = await extract_intent_and_slots(req)
        user_id = self._extract_user_id(req)
        intent_dict["data"]["userId"] = user_id
        if hasattr(req, "active"):
            intent_dict["data"]["active"] = req.active
        intent = Intent(**intent_dict)

        agent_name = (intent.app or "").lower()
        
        if agent_name in self.agents:
            agent_resp = await self.agents[agent_name].handle(intent)
            return agent_resp, agent_name

        return AgentResponse(
            success=False,
            message="No matching agent found."
        ), agent_name