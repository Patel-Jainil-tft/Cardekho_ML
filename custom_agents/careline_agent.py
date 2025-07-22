from mod.models import Intent, AgentResponse

class CarelineAgent:
    REQUIRED_FIELDS = ["marriage_status"]
    #REQUIRED_FIELDS = ["updated_email_id", "updated_mobile_number", "salary_account_number", "IFSC_code", "marriage_status_to"]

    
    def handle(self, intent: Intent) -> AgentResponse:
        missing = [field for field in self.REQUIRED_FIELDS if not intent.data.get(field)]
        if missing:
            return AgentResponse(
                success=False,
                message=f"Please provide: {', '.join(missing)}",
                missing=", ".join(missing)
            )
        # In a real implementation, forward to MCP here
        return AgentResponse(
            success=True,
            message="Ready for MCP execution",
            data={field: intent.data[field] for field in self.REQUIRED_FIELDS}
        )