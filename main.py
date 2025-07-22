from fastapi import FastAPI
from mod.models import QueryRequest
from core.master_agent import MasterAgent
from integration.mcp_client import MCPServerClient

app = FastAPI()
master_agent = MasterAgent()
mcp_client = MCPServerClient(base_url="http://localhost:8001")  # Update to real server if/when ready

@app.post("/query")
async def query_agents(query: QueryRequest):
    agent_resp, agent_name = await master_agent.route_request(query)
    print(f"Agent response from {agent_name}: {agent_resp}")
    if agent_resp.success:
        return {"status": "ok", "message": agent_resp.message, "data": agent_resp.data}
    else:
        return {"status": "error", "message": agent_resp.message, "missing": agent_resp.missing}

