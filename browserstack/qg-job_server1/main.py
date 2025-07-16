from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List, Tuple
import uuid
import threading
import time
import random
import os
import requests

app = FastAPI()

# ------------------------------
# Job Models
# ------------------------------

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
    # Optional fields for BrowserStack video/log URLs can be added here

class JobGroup:
    def __init__(self, app_version_id: str, target: str):
        self.app_version_id = app_version_id
        self.target = target
        self.jobs: List[Job] = []
        self.running = False

# ------------------------------
# In-Memory Storage
# ------------------------------

job_groups: Dict[Tuple[str, str], JobGroup] = {}
completed_jobs: Dict[str, Job] = {}
lock = threading.Lock()

# ------------------------------
# BrowserStack Test Runner
# ------------------------------

def run_browserstack_test(job):
    bs_user = os.getenv("BS_USERNAME")
    bs_key = os.getenv("BS_ACCESS_KEY")

    if not bs_user or not bs_key:
        print("BrowserStack credentials not set in environment variables.")
        job.status = "failed"
        return

    print(f"Starting BrowserStack test for job {job.job_id}...")

    try:
        # NOTE: Replace this with actual API call for your AppWright tests on BrowserStack
        response = requests.post(
            "https://api.browserstack.com/automate/sessions.json",  # Example placeholder endpoint
            auth=(bs_user, bs_key),
            json={
                "build": f"Qualgent Build - {job.app_version_id}",
                "name": f"Job {job.job_id} - Test {job.test_path}",
                "browser": "chrome",
                "os": "Windows",
                "os_version": "11",
                # Add any additional needed config here
            }
        )

        if response.status_code != 200:
            print(f"Failed to start BrowserStack test: {response.status_code} {response.text}")
            job.status = "failed"
            return

        session_id = response.json().get("automation_session", {}).get("session_id")
        if not session_id:
            print("No session_id returned from BrowserStack")
            job.status = "failed"
            return

        # Poll for session status
        timeout = 300
        poll_interval = 10
        start_time = time.time()

        while time.time() - start_time < timeout:
            status_resp = requests.get(
                f"https://api.browserstack.com/automate/sessions/{session_id}.json",
                auth=(bs_user, bs_key)
            )
            if status_resp.status_code != 200:
                print(f"Error polling BrowserStack session: {status_resp.status_code}")
                job.status = "failed"
                return

            status_data = status_resp.json().get("automation_session", {})
            status = status_data.get("status")

            print(f"BrowserStack session status: {status}")

            if status in ("completed", "passed", "failed"):
                job.status = "success" if status == "passed" else "failed"
                # Optional: save video/log urls
                # job.video_url = status_data.get("video_url")
                break

            time.sleep(poll_interval)
        else:
            print("BrowserStack test timed out")
            job.status = "failed"

    except Exception as e:
        print(f"Exception running BrowserStack test: {e}")
        job.status = "failed"

# ------------------------------
# Background Job Processor
# ------------------------------

def job_processor():
    while True:
        try:
            with lock:
                # Find a job group that is not running with queued jobs
                for key, group in job_groups.items():
                    if not group.running and any(job.status == "queued" for job in group.jobs):
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
                    print(f"Starting job {job.job_id} in group {key}")
                    job.status = "running"

                if job.target == "browserstack":
                    run_browserstack_test(job)
                else:
                    # Simulated run for emulator/device
                    time.sleep(2)
                    failed = False
                    if random.random() < 0.2:
                        failed = True

                    with lock:
                        if failed:
                            job.retries += 1
                            print(f"Job {job.job_id} failed (retry {job.retries}/{job.max_retries})")
                            if job.retries > job.max_retries:
                                job.status = "failed"
                                print(f"Job {job.job_id} failed permanently.")
                            else:
                                job.status = "queued"
                                print(f"Job {job.job_id} will retry.")
                        else:
                            job.status = "success"
                            print(f"Job {job.job_id} succeeded.")

                with lock:
                    if job.status in ("success", "failed"):
                        completed_jobs[job.job_id] = job

            with lock:
                if all(job.status in ("success", "failed") for job in group.jobs):
                    print(f"All jobs in group {key} done. Removing group.")
                    del job_groups[key]
                else:
                    group.running = False

        except Exception as e:
            print(f"Exception in job processor: {e}")
            time.sleep(1)

threading.Thread(target=job_processor, daemon=True).start()

# ------------------------------
# API Endpoints
# ------------------------------

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
            group = JobGroup(app_version_id=job.app_version_id, target=job.target)
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
                        "job": job.dict()
                    }
        if job_id in completed_jobs:
            job = completed_jobs[job_id]
            return {
                "job_id": job.job_id,
                "status": job.status,
                "job": job.dict()
            }

    return {"error": "Job not found"}
