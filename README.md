# Backend Service Setup

1. Install dependencies:

   pip install fastapi uvicorn pydantic

2. Run backend:

   uvicorn main:app --host 0.0.0.0 --port 8000 --reload

3. API Endpoints:

   - POST /submit-job : Submit a test job (org_id, app_version_id, test_path, priority, target)
   - GET /status/{job_id} : Get job status by job ID

4. Jobs with same app_version_id and target are grouped and run sequentially on the same device.
5. Jobs will retry up to 3 times if they fail.