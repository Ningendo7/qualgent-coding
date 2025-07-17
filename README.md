# ⚡ QualGent BrowserStack Test Runner

This project is a CLI + Backend tool to queue and run automated cross-platform tests on BrowserStack. It allows you to trigger tests for Android, iOS, or Windows from a backend service and run them via Dockerized GitHub Actions.

---

## 🧱 Project Structure

```
.
├── backend/                   # FastAPI backend for job queuing and tracking
│   ├── main.py
│   ├── job_manager.py
│   ├── test_runner.py
│   ├── models.py
│   └── Dockerfile.backend
├── tests/                     # JS-based BrowserStack test files
│   └── onboarding.spec.js
├── Dockerfile.testrunner     # Node.js container to run BrowserStack tests
├── docker-compose.yaml       # Defines backend and testrunner services
├── .github/
│   └── workflows/
│       └── browserstack-test.yml
├── package.json              # Node dependencies for the test runner
├── .env                      # Environment variables for BrowserStack
└── README.md                 # You are here
```

---

## 🚀 Prerequisites

- Docker & Docker Compose
- Node.js (for local test runner)
- Python 3.10+ (if running backend without Docker)
- [BrowserStack account](https://www.browserstack.com/users/sign_up)

---

## 🔐 Environment Variables

Create a `.env` file in your project root:

```
BS_USERNAME=your_browserstack_username
BS_ACCESS_KEY=your_browserstack_access_key
```

These credentials are used by both the backend and the test runner.

---

## 🧪 Running Tests Manually (CLI)

You can run a BrowserStack test directly using Docker:

```bash
docker compose run --rm testrunner android "Cristiano Ronaldo"
```

Supported platforms: `android`, `ios`, `windows`  
Search text: Any string to verify it appears on a Wikipedia page.

---

## 🔙 Starting the Backend

The backend service queues and monitors BrowserStack test jobs.

### Run with Docker Compose:

```bash
docker compose up --build backend
```

By default, it will be available at: `http://localhost:8000`

### Example usage:

```bash
# Queue a test job
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" \
  -d '{"platform": "android", "searchText": "Cristiano Ronaldo"}'

# Check job status
curl http://localhost:8000/status/<JOB_ID>
```

---

## 🤖 GitHub Actions Automation

When you push to the repo, the test will automatically run via GitHub Actions.

### Example

In `.github/workflows/browserstack-test.yml`:

```yaml
- name: Run BrowserStack test
  run: docker compose run --rm testrunner android "Juventus"
```

You can customize this step to run any combination of platform and search term.

---

## 📦 Cleanup

To remove containers, volumes, and networks created by Docker Compose:

```bash
docker compose down --volumes
```

