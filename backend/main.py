from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List, Tuple, Optional
import uuid
import threading
import time
import random
import os
import requests

app = FastAPI()

# Job request and job models
class JobRequest(BaseModel):
    org_id: str
    app_version_id: str
    test_path: str
    priority: int
    target: str

class Job(BaseModel):
    job_id: str
    org_id: str
    app_version_id: str
    test_path: str
    priority: int
    target: str
    status: str  # queued, running, success, failed
    retries: int = 0
    max_retries: int = 3
    video_url: Optional[str] = None
    logs_url: Optional[str] = None

class JobGroup:
    def __init__(self, app_version_id: str, target: str):
        self.app_version_id = app_version_id
        self.target = target
        self.jobs: List[Job] = []
        self.running = False

job_groups: Dict[Tuple[str, str], JobGroup] = {}
completed_jobs: Dict[str, Job] = {}
lock = threading.Lock()

def run_browserstack_test(job: Job):
    bs_user = os.getenv("BS_USERNAME")
    bs_key = os.getenv("BS_ACCESS_KEY")
    if not bs_user or not bs_key:
        print("BrowserStack credentials missing")
        job.status = "failed"
        return

    print(f"Running BrowserStack test for job {job.job_id}")

    # Here you invoke your actual node test script or BrowserStack API call.
    # For demo, simulate test run:
    time.sleep(5)  # simulate test execution time

    # Simulate random success/fail
    if random.random() < 0.15:
        job.status = "failed"
        job.video_url = None
        job.logs_url = None
        print(f"Job {job.job_id} failed")
    else:
        job.status = "success"
        # Dummy URLs to BrowserStack videos/logs (replace with actual API call results)
        job.video_url = f"https://automate.browserstack.com/sessions/{job.job_id}/video"
        job.logs_url = f"https://automate.browserstack.com/sessions/{job.job_id}/logs"
        print(f"Job {job.job_id} succeeded")

def job_processor():
    while True:
        try:
            with lock:
                for key, group in job_groups.items():
                    if not group.running and any(j.status == "queued" for j in group.jobs):
                        group.running = True
                        break
                else:
                    group = None

            if not group:
                time.sleep(1)
                continue

            for job in group.jobs:
                with lock:
                    if job.status != "queued":
                        continue
                    job.status = "running"
                    print(f"Starting job {job.job_id} in group {key}")

                if job.target == "browserstack":
                    run_browserstack_test(job)
                else:
                    # Simulated run for other targets (emulators/devices)
                    time.sleep(3)
                    if random.random() < 0.2:
                        job.status = "failed"
                    else:
                        job.status = "success"

                with lock:
                    if job.status in ("success", "failed"):
                        completed_jobs[job.job_id] = job

            with lock:
                if all(j.status in ("success", "failed") for j in group.jobs):
                    print(f"All jobs done in group {key}. Removing group.")
                    del job_groups[key]
                else:
                    group.running = False
        except Exception as e:
            print(f"Job processor error: {e}")
            time.sleep(1)

threading.Thread(target=job_processor, daemon=True).start()

@app.post("/submit-job")
def submit_job_api(job_data: JobRequest):
    job = Job(
        job_id=str(uuid.uuid4()),
        org_id=job_data.org_id,
        app_version_id=job_data.app_version_id,
        test_path=job_data.test_path,
        priority=job_data.priority,
        target=job_data.target,
        status="queued"
    )

    key = (job.app_version_id, job.target)
    with lock:
        group = job_groups.get(key)
        if not group:
            group = JobGroup(job.app_version_id, job.target)
            job_groups[key] = group
        group.jobs.append(job)

    return {"job_id": job.job_id, "status": job.status}

@app.get("/status/{job_id}")
def get_job_status(job_id: str):
    with lock:
        for group in job_groups.values():
            for job in group.jobs:
                if job.job_id == job_id:
                    return {
                        "job_id": job.job_id,
                        "status": job.status,
                        "video_url": job.video_url,
                        "logs_url": job.logs_url,
                        "job": job.dict()
                    }
        if job_id in completed_jobs:
            job = completed_jobs[job_id]
            return {
                "job_id": job.job_id,
                "status": job.status,
                "video_url": job.video_url,
                "logs_url": job.logs_url,
                "job": job.dict()
            }
    return {"error": "Job not found"}
