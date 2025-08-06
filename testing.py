# testing.py
import asyncio
from bullmq import Queue

async def main():
    queue = Queue("request_2_nlp")  # Or your actual REQUEST_2_NLP queue name

    payload = {
        "message": "pls show list of repotees",
        "jobId": "684921e55caa9eecf4c9e011",
        "userId": "65c0d045802b48425f607e3c",
        "chatPlatform": "webSocket",
        "organizationId": "66dabc99f97892858e782663",
        "incorrect": "",
        "chatHistory": "Today",
        "userRole": "employee",
        "applicable": ["darwinbox", "careline"],
        "token": {
            "darwinbox": {
                "employee_no": "10067563"
            }
        },
        "active": 0
    }

    await queue.add("MLJob", payload)
    print("✅ Job pushed to queue.")

asyncio.run(main())
