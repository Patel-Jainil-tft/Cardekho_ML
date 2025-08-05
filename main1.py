# main1.py
import os
import asyncio
import logging
from redis.asyncio import Redis
from bullmq import Worker, Queue, Job
from core.master_agent import MasterAgent
import json
from bullmq import Queue
# Setup Redis connection info
REDIS_HOST = os.environ.get("REDIS_HOST_NAME", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT_NUMBER", 6379))
REDIS_PASS = os.environ.get("REDIS_PASSWORD", None)
logging.basicConfig(level=logging.INFO)

def get_worker_and_request():
    """
    Retrieves the appropriate worker and request queue settings based on the current environment.

    Args:
        None: The function fetches environment variables automatically.

    Raises:
        KeyError: If required environment variables ('PROD_NLP_2_WORKER', 'STAGING_NLP_2_WORKER', etc.) are missing.
        ValueError: If 'ENVIRONMENT' is set to an invalid value.

    Returns:
        Tuple[str, str]: A tuple containing ('nlp_2_worker', 'request_2_nlp') corresponding to the selected environment.
    """
    nlp_2_worker = None
    request_2_nlp = None
    ENVIRONMENT = os.environ.get("ENVIRONMENT")
    if ENVIRONMENT == "prod":
        #logger.info("\n======== prod server ========")
        nlp_2_worker = os.environ.get("PROD_NLP_2_WORKER")
        request_2_nlp = os.environ.get("PROD_REQUEST_2_NLP")
    elif ENVIRONMENT == "staging":
        #logger.info("\n======== staging server ========")
        nlp_2_worker = os.environ.get("STAGING_NLP_2_WORKER")
        request_2_nlp = os.environ.get("STAGING_REQUEST_2_NLP")
    else:
        print("Invalid environment.")
    return nlp_2_worker, request_2_nlp
NLP_2_WORKER, REQUEST_2_NLP = get_worker_and_request()

# Initialize master agent
master_agent = MasterAgent()

async def handle_job(job: Job, _: str):
    logging.info(f"📥 Received job ID: {job.id}")
    
    try:
        agent_resp, agent_name = await master_agent.route_request(job.data)

        output_queue = Queue(NLP_2_WORKER, {
            "host": REDIS_HOST,
            "port": REDIS_PORT,
            "password": REDIS_PASS
        })
        
        print(f"🔄 Pushing response to output queue: {NLP_2_WORKER}")
        response_payload = {
            "jobId": job.id,
            "agent": agent_name,
            "status": "ok" if agent_resp.success else "error",
            "message": agent_resp.message or "",
            "missing": agent_resp.missing if hasattr(agent_resp, "missing") else "",
            "userId": agent_resp.user_id,
            "organizationId": agent_resp.organization_id,
            "userRole": getattr(agent_resp, "user_role", "employee"),
            "jobId": getattr(agent_resp, "job_id", "12345")
        }

        print("📤 Response Payload to Output Queue:")
        print("📦 Final payload pushed to output queue:")
        print(json.dumps(response_payload, indent=2))
 

        await output_queue.add("MLJobOutput", response_payload)

        # await output_queue.add("MLJobOutput", {
        #     "jobId": job.id,
        #     "agent": agent_name,
        #     "status": "ok" if agent_resp.success else "error",
        #     "message": agent_resp.message or "",
        #     "data": agent_resp.data if agent_resp.success else {},
        #     "missing": agent_resp.missing if hasattr(agent_resp, "missing") else "",
        #     "userId": agent_resp.user_id,
        #     "organizationId": agent_resp.organization_id,
        #     "userRole": agent_resp.user_role,
        #     "jobId": agent_resp.job_id,

        # })



    except Exception as e:
        logging.exception(f"❌ Error processing job {job.id}")

async def main():
    logging.info("🚀 Starting worker...")

    redis_conn = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASS
    )

    # Validate Redis connection
    if not await redis_conn.ping():
        logging.error("❌ Redis connection failed!")
        return

    await redis_conn.close()

    # Start BullMQ worker
    worker = Worker(
        REQUEST_2_NLP,
        handle_job,
        opts={"connection": {
            "host": REDIS_HOST,
            "port": REDIS_PORT,
            "password": REDIS_PASS
        }}
    )

    logging.info(f"✅ Worker listening on queue: {REQUEST_2_NLP}")
    await asyncio.Future()  # Keep running

if __name__ == "__main__":
    asyncio.run(main())
