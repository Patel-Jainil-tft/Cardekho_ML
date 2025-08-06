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
        try:
            resp = self.mcp_client.fetch_tools()
            self.mcp_tools_list = resp.get("result", {}).get("tools", [])
        except Exception:
            logging.exception("Failed to fetch tools from MCP.")
            self.mcp_tools_list = []

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
        try:
            intent_data = await extract_parameters(intent.user_input)
            intent.data.update(intent_data)
            user_prompt = (
                f"user input: {intent.user_input}\nExtracted fields: {intent.data}\ncategory: {intent.category}\n"
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
            active = intent.data.pop("active", None)
            mcp_payload = {"userId": user_id, "active": active}
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
                mcp_payload["updateData"] = intent.data
            try:
                mcp_result = self.mcp_client.call_action(tool_name, mcp_payload)
            except Exception:
                logging.exception("Exception during MCP action call.")
                mcp_result = {"status": "error", "error": "MCP call failed"}
            try:
                human_message = await format_mcp_response(mcp_result)
            except Exception:
                logging.exception("Failed to format MCP response.")
                human_message = "Could not generate user-friendly response."
            return AgentResponse(
                success=True,
                message=human_message,
                tool=tool_name,
                user_id=user_id,
                organization_id=intent.organizationId,
                jobId=intent.jobId,
                userRole=intent.userRole
            )
        except Exception:
            logging.exception("DarwinBoxAgent handle() error.")
            return AgentResponse(success=False, message="Exception in DarwinBoxAgent")
