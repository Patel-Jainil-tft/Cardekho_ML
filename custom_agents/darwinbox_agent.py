from intent_classifier.action_resolver import ACTION_SCHEMA
from mod.models import Intent, AgentResponse


class DarwinBoxAgent:
    def handle(self, intent: Intent) -> AgentResponse:
        action = intent.action
        possible_fields = ACTION_SCHEMA.get(action, [])
        provided = [field for field in possible_fields if intent.data.get(field) not in [None, '', False, [], 0]]
        if not provided:
            return AgentResponse(
                success=False,
                message=f"Please provide at least one of: {', '.join(possible_fields)}",
                missing=", ".join(possible_fields)
            )
        return AgentResponse(
            success=True,
            message="Ready for MCP execution",
            data={field: intent.data[field] for field in provided}
        )
