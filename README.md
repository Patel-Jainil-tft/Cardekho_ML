System Architecture
Core workflow:

Input: The platform accepts a rich, metadata-enriched query payload representing a user query from upstream chat or web frontends.

Master Agent: All requests are routed through the Master Agent, which uses an OpenAI agent as the core reasoning/NLU engine. This agent classifies the intent, extracts action and slots, and determines the downstream resource.

Agent Pool: Depending on the action and extracted parameters, the Master Agent routes the query to the appropriate business/domain agent (DarwinBoxAgent, CarelineAgent, etc.) for logic execution.

MCP Tool Invocation: For queries requiring backend computation or records access, the agent invokes tools on the backend MCP server (compliant JSON-RPC invocation; see Postman screenshot).

Response: A unified response object is returned, with robust error reporting and validation.

Agents / Components
Master Agent: Orchestrates all intent extraction and downstream agent/tool selection, using the OpenAI Agents SDK.

DarwinBoxAgent & Others: Implement business-logic, performing validations and executing mapped actions.

MCPServerClient: Handles all backend MCP tool calls (for actions like viewUAN, viewListOfReportees) via JSON-RPC.

Highlights
Modular, extensible agent design for onboarding new domains (CarelineAgent, OtherAgent, etc.)

Pluggable orchestration logic to support new business actions and NLU improvements.

Native support for async, scalable FastAPI deployment.

Seamless, contract-true integration with backend MCP as seen in the example Postman request.

How It Works
Request: Receives user query + metadata (see left-most JSON in the diagram).

Master Agent: Uses OpenAI agent to extract (action, app, category, slots) per schema.

Agent or Tool:

If business logic: delegates to DarwinBoxAgent or another agent.

If tool/record fetch: invokes MCPServerClient to backend /mcp endpoint using a JSON-RPC payload.

Response: Unified and error-tolerant response sent back upstream.

Sample MCP Tool Call
json
{
  "method": "tools/call",
  "params": {
    "name": "viewUAN",
    "arguments": {
      "userId": "10067563"
    }
  }
}
Directory Structure
main.py: FastAPI entrypoint.

core/master_agent.py: Central orchestrator, select agents/tools.

orchestration.py: OpenAI agent definition, intent extraction.

custom_agents/: Domain business agents (e.g., DarwinBoxAgent).

integration/mcp_client.py: Backend MCP client.

mod/models.py: Request/response models.

Setup
Clone the repo.

Install dependencies (pip install -r requirements.txt)

Set your OPENAI_API_KEY in your environment.

Start the FastAPI server.

Test MCP tool flow using /query endpoint or Postman as shown above.