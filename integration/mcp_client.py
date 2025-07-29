import requests
import logging

class MCPServerClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def call_action(self, tool_name: str, arguments: dict):
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        try:
            resp = requests.post(
                self.base_url,
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                },
                timeout=20
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logging.exception(f"Error in call_action for tool {tool_name}")
            return {"status": "error", "err": str(e), "tool": tool_name, "payload": data}

    def fetch_tools(self):
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        try:
            resp = requests.post(
                self.base_url,
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                },
                timeout=10
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logging.error(f"Error fetching tools: {e}")
            return {"status": "error", "err": str(e)}