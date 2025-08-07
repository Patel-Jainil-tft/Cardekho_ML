import os
import logging
from mod.models import QueryRequest, AgentResponse, Intent
from orchestration import extract_intent_and_slots
from custom_agents.darwinbox_agent import DarwinBoxAgent
from custom_agents.careline_agent import CarelineAgent
from integration.mcp_client import MCPServerClient
from db.mongo import save_agent_response
import datetime

logging.basicConfig(level=logging.INFO)

class MasterAgent:
    def __init__(self):
        self.agents = {
            "darwinbox": DarwinBoxAgent(),
            "careline": CarelineAgent(),
        }
        base_url = os.getenv("MCP_SERVER_URL", "http://192.168.112.32:3001/mcp")
        self.mcp_client = MCPServerClient(base_url=base_url)
        try:
            tools_resp = self.mcp_client.fetch_tools()
            self.mcp_tools_list = tools_resp.get("result", {}).get("tools", [])
            logging.info(f"Available MCP Tools: {[t['name'] for t in self.mcp_tools_list]}")
        except Exception:
            logging.exception("Failed to fetch MCP tools.")
            self.mcp_tools_list = []

    @staticmethod
    def _extract_user_id(req):
        token = getattr(req, "token", None)
        if token and isinstance(token, dict):
            dbx = token.get("darwinbox")
            if dbx and isinstance(dbx, dict):
                emp_no = dbx.get("employee_no")
                if emp_no:
                    return emp_no
        return req.userId or ""

    async def route_request(self, req: QueryRequest):
        try:
            if isinstance(req, dict):
                req = QueryRequest(**req)
            intent_dict = await extract_intent_and_slots(req)
            user_id = self._extract_user_id(req)
            organization_id = req.organizationId or ""
            intent_dict["user_input"] = req.message
            intent = Intent(**intent_dict)
            intent.user_input = req.message
            intent.data["userId"] = user_id
            intent.organizationId = req.organizationId or ""
            intent.jobId = req.jobId
            intent.userRole = req.userRole or ""

            if hasattr(req, "active"):
                intent.data["active"] = req.active

            agent_name = (intent.app or "").lower()
            intent.organizationId = organization_id
            intent.jobId = req.jobId
            intent.userRole = req.userRole or ""

            if agent_name in self.agents:
                agent_resp = await self.agents[agent_name].handle(intent)
                final_payload = {
                "jobId": intent.jobId,
                "agentName": agent_name,
                "tool": getattr(agent_resp, "tool",""),  
                "userId": agent_resp.user_id,
                "organizationId": agent_resp.organization_id,
                "userRole": agent_resp.user_role,
                "status": "ok" if agent_resp.success else "error",
                "message": agent_resp.message,
                "data": agent_resp.data,
                "missing": getattr(agent_resp, "missing", ""),
                "userInput": intent.user_input,
                "intent": {
                    "app": intent.app,
                    "category": intent.category,
                    "action": intent.action,
                    "data": intent.data,  
                }
            }
                try:
                    save_agent_response(final_payload)
                except Exception:
                    logging.exception("Failed to save agent response to MongoDB.")
                return agent_resp, agent_name
            logging.error("No matching agent found for agent_name=%s", agent_name)
            return AgentResponse(success=False, message="No matching agent found."), agent_name
        except Exception:
            logging.exception("Error in agent routing.")
            return AgentResponse(success=False, message="MasterAgent exception."), "unknown"