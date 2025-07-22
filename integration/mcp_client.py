import requests

class MCPServerClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def call_action(self, tool_name: str, arguments: dict):
    # arguments must be {"userId": ...}
        data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
        url = self.base_url  # no /actions/... just /mcp
        print(url)
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
            print(resp)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"status": "error", "err": str(e), "tool": tool_name, "payload": data}
        

        