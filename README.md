This repository implements a modular agent orchestration framework using **OpenAI’s Agents SDK** to route HR-related queries, perform backend computations, and return structured, reliable responses.

---

## 📌 System Architecture

### 🔁 Core Workflow

1. **Input**  
   Receives a metadata-rich query payload from upstream chat or web platforms.

2. **Master Agent**  
   Acts as the central orchestrator. Uses an OpenAI Agent (via `openai.Agent`, `Runner`) to:
   - Classify user intent
   - Extract action, app, category, and relevant parameters
   - Route to appropriate domain logic or tool

3. **Agent Pool**  
   Based on the extracted intent, routes the request to a domain-specific business agent such as:
   - `DarwinBoxAgent`
   - `CarelineAgent`
   - `OtherAgent` (extensible)

4. **MCP Tool Invocation**  
   For backend data retrieval or business actions, calls JSON-RPC-compliant tools via the MCP server using a unified interface (`MCPServerClient`).

5. **Response**  
   Returns a standardized response with validation and error metadata.

---

## 🧱 Components & Responsibilities

### 🔹 `MasterAgent`
- Central decision-maker
- Uses OpenAI Agent for NLU + tool reasoning
- Forwards request to downstream logic/tool

### 🔹 `DarwinBoxAgent`, `CarelineAgent`, etc.
- Execute specific business logic
- Perform validations
- Respond with structured data

### 🔹 `MCPServerClient`
- Communicates with backend MCP tools
- Follows JSON-RPC contract
- Example request:

```json
{
  "method": "tools/call",
  "params": {
    "name": "viewUAN",
    "arguments": {
      "userId": "10067563"
    }
  }
}
