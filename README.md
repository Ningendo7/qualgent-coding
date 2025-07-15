# QualGent Backend Coding Challenge

## Project Overview

This project implements a test job orchestration platform for AppWright tests.  
It includes:  
- A backend service (`qg-job_server`) to queue, group, and schedule test jobs across devices and emulators.  
- A CLI tool (`qg-job`) for submitting jobs and checking their status.  
- A GitHub Actions workflow that submits tests on push and polls for completion.

---

## Setup Instructions

### Prerequisites

- Python 3.8+  
- Redis or PostgreSQL (optional; currently uses in-memory queue)  
- Git

---
### Configuring Backend URL

By default, the CLI tool uses `http://localhost:8000` to connect to the backend service.

- If you run the CLI and backend on the same machine (e.g., in GitHub Actions or local Docker), no changes are needed.
- If you want to run the CLI on a different machine (like your local computer) and connect to a remote backend server (e.g., an EC2 instance), you should update the 'BACKEND_URL' variable in the CLI code to point to the backend’s accessible IP or hostname.  

Example:
BACKEND_URL = "http://<your-ip>:8000"

---

### Backend Service

1. Navigate to the backend folder:
   ```bash
   cd qg-job_server
Install dependencies:
pip install -r requirements.txt

Run the backend server:
uvicorn main:app --host 0.0.0.0 --port 8000

---
OPTIONAL: RUN BACKEND USING DOCKER
---
cd qg-job_server
docker build -t qg-job-server .
docker run -p 8000:8000 qg-job-server
---
### CLI Tool
Navigate to the CLI folder:
cd qg-job
Install dependencies:
pip install -r requirements.txt

Submit a job:
python qg-job.py submit --org-id qualgent --app-version-id xyz123 --test tests/onboarding.spec.js --priority 1 --target emulator
Check job status:
python qg-job.py status --job-id <job_id>

---

Architecture Diagram

+-------------+       +------------------+       +--------------+
|   CLI Tool  | <---> | Backend Service  | <---> | Job Queueing |
+-------------+       +------------------+       +--------------+
       |                      |                         |
       |                      |               Groups jobs by app_version_id and target
       |                      |                         |
       v                      v                         v
 Runs submit/status      Receives jobs,          Assigns jobs to devices
   commands             schedules execution

-------
### Grouping and Scheduling
Jobs submitted with the same app_version_id and target are grouped together to minimize app reinstall overhead.

The backend processes job groups sequentially per device target but supports parallel groups across different targets and orgs.

Jobs have priority and retry logic to handle failures and optimize execution scheduling.

Running an End-to-End Test
Make sure the backend service is running and accessible.

### Submit a test job using the CLI:

python qg-job.py submit --org-id qualgent --app-version-id xyz123 --test tests/onboarding.spec.js --priority 1 --target emulator
Save the returned job_id.
---
Poll for job status:
python qg-job.py status --job-id <job_id>
Repeat until job status is success or failed.

 Alternatively, push to your GitHub repo to trigger the GitHub Actions workflow.
It will automatically submit the job and poll for status.
---

### Final Notes
The backend uses an in-memory queue for simplicity.
For production, consider integrating Redis or PostgreSQL for durability.

Ensure your backend server is accessible from the CLI or GitHub Actions.
(i.e., check firewall/security group settings on server if needed.)

The architecture is modular and designed for scalability. You can extend:

Retry mechanisms

Monitoring endpoints

Device scheduling strategies

Thanks for reviewing this challenge!
Feel free to reach out if you have questions or feedback.