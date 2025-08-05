import os
import logging
from fastapi import FastAPI
from mod.models import QueryRequest
from core.master_agent import MasterAgent
from queue import Queue

# Global Queue
query_queue = Queue()

app = FastAPI()
master_agent = MasterAgent()

@app.post("/query")
async def query_agents(query: QueryRequest):
    agent_resp, agent_name = await master_agent.route_request(query)
    logging.info(f"Agent response from {agent_name}: {agent_resp}")
    
    if agent_resp.success:
        return {"status": "ok", "message": agent_resp.message, "data": agent_resp.data}
    else:
        return {"status": "error", "message": agent_resp.message, "missing": agent_resp.missing or ""}
