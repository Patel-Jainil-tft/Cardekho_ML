import logging
import os
from mod.models import Intent, AgentResponse
from agents import Agent, Runner
from integration.mcp_client import MCPServerClient
from custom_agents.response_formatter import format_mcp_response
from extractors.params_extraction import extract_parameters
logging.basicConfig(level=logging.INFO)

class DarwinBoxAgent:
    def __init__(self):
        self.mcp_client = MCPServerClient(base_url=os.getenv("MCP_SERVER_URL", "http://localhost:3001/mcp"))
        resp = self.mcp_client.fetch_tools()
        self.mcp_tools_list = resp.get("result", {}).get("tools", [])
        self.tool_names = [tool["name"] for tool in self.mcp_tools_list]
        
        instructions = (
            "You are the DarwinBox Tool Selector agent for HR workflows.\n"
            "Given an HR intent, extracted action, and parameters, "
            "Based upon the given information choose DarwinBox MCP tool name that best represents what the user wants to do from the supported list. If it is not available in supported list simply return NONE\n"
            "Respond ONLY with the tool name as a plain string—no explanation, JSON, or markdown.\n"
            "Supported tools:\n" +
            "\n".join(f"- {tool}" for tool in self.tool_names)
        )

        self.tool_agent = Agent(
            name="DarwinBoxToolAgent",
            instructions=instructions,
            model="gpt-4o-mini"
        )

    async def handle(self, intent: Intent) -> AgentResponse:
        intent_data = await extract_parameters(intent.user_input)
        intent.data.update(intent_data)
        user_prompt = (
            f"user input: {intent.action}\nExtracted fields: {intent.data}\ncategory: {intent.category}\n"
            "Which DarwinBox MCP tool from the supported list is the best match?"
        )
        result = await Runner.run(self.tool_agent, user_prompt)
        tool_name = result.final_output.strip().strip('"').strip("'")

        user_id = intent.data.pop("userId", None)
        if not user_id:
            return AgentResponse(
                success=False,
                message="userId is required for DarwinBox operations.",
                missing="userId"
            )

        # Safely remove userId and active from intent.data after extracting
        active = intent.data.pop("active", None)
        print(f"Extracted ACTIVE status: {active}")

        mcp_payload = {"userId": user_id, "active": active}
        print(f"intent: {intent}")

        if tool_name.lower() == "viewreimbursementstatus":
            date_val = intent.data.get("extracted_result", {}).get("appliedDate")
            if not date_val:
                return AgentResponse(
                    success=False,
                    message="Please provide the date for which you want to check your reimbursement status.",
                    missing="appliedDate"
                )
            mcp_payload["appliedDate"] = date_val
        elif tool_name.lower() == "updateuserprofile":
            print(f"Extracted data for update: {intent.data}")
            mcp_payload["updateData"] = intent.data

        logging.info(f"Selected tool: {tool_name} with payload: {mcp_payload}")
        print(f"Selected tool: {tool_name} with payload: {mcp_payload}")
        print(f"📥 intent: {intent}")
        mcp_result = self.mcp_client.call_action(tool_name, mcp_payload)
        human_message = await format_mcp_response(mcp_result)

        return AgentResponse(
            success=True,
            message=human_message,
            tool=tool_name,
            #data=mcp_result,
            user_id=user_id,
            organization_id=intent.organizationId,
            jobId=intent.jobId,
            userRole=intent.userRole
        )