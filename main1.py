import os
import asyncio
import logging
from redis.asyncio import Redis
from bullmq import Worker, Queue, Job
from core.master_agent import MasterAgent
import json

logging.basicConfig(level=logging.INFO)

REDIS_HOST = os.environ.get("REDIS_HOST_NAME", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT_NUMBER", 6379))
REDIS_PASS = os.environ.get("REDIS_PASSWORD", None)

def get_worker_and_request():
    ENVIRONMENT = os.environ.get("ENVIRONMENT")
    if ENVIRONMENT == "prod":
        nlp_2_worker = os.environ.get("PROD_NLP_2_WORKER")
        request_2_nlp = os.environ.get("NLP_2_WORKER")
    elif ENVIRONMENT == "staging":
        logging.info("\n======== staging server ========")
        nlp_2_worker = os.environ.get("STAGING_NLP_2_WORKER")
        request_2_nlp = os.environ.get("NLP_2_WORKER")
    else:
        logging.error("Invalid environment.")
        raise ValueError("Invalid ENVIRONMENT variable.")
    return nlp_2_worker, request_2_nlp

NLP_2_WORKER, REQUEST_2_NLP = get_worker_and_request()
logging.info(f"NLP_2_WORKER: {NLP_2_WORKER}, REQUEST_2_NLP: {REQUEST_2_NLP}")

master_agent = MasterAgent()

async def handle_job(job: Job, queue_name: str):
    logging.info(f"Received job ID: {job.id}")
    try:
        agent_resp, agent_name = await master_agent.route_request(job.data)
        output_queue = Queue(NLP_2_WORKER, {
            "host": REDIS_HOST,
            "port": REDIS_PORT,
            "password": REDIS_PASS
        })

        response_payload = {
            "jobId": getattr(agent_resp, "jobId", job.data.get("jobId", "")),
            "agent": agent_name,
            "status": "ok" if agent_resp.success else "error",
            "message": agent_resp.message or "",
            "missing": getattr(agent_resp, "missing", ""),
            "userId": agent_resp.user_id,
            "organizationId": agent_resp.organization_id,
            "userRole": getattr(agent_resp, "user_role", "employee")        }

        logging.info(f"Response Payload to Output Queue: {json.dumps(response_payload, indent=2)}")
        await output_queue.add("MLJobOutput", response_payload)

    except Exception as e:
        logging.exception(f"Error processing job {job.id}")
        # Optionally, report error to output queue or monitoring

async def main():
    logging.info("Starting worker...")
    try:
        redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS)
        if not await redis_conn.ping():
            logging.error("Redis connection failed!")
            return
        await redis_conn.close()
        worker = Worker(
            REQUEST_2_NLP,
            handle_job,
            opts={"connection": {
                "host": REDIS_HOST,
                "port": REDIS_PORT,
                "password": REDIS_PASS
            }}
        )
        logging.info(f"Worker listening on queue: {REQUEST_2_NLP}")
        await asyncio.Future()
    except Exception:
        logging.exception("Worker crashed during startup.")

if __name__ == "__main__":
    asyncio.run(main())
