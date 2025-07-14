import argparse
import requests
import sys
import time

BACKEND_URL = "http://18.212.231.237:8000"  # Change if your backend URL differs   

def submit_job(args):
    payload = {
        "org_id": args.org_id,
        "app_version_id": args.app_version_id,
        "test_path": args.test,
        "priority": args.priority,
        "target": args.target
    }
    try:
        response = requests.post(f"{BACKEND_URL}/submit-job", json=payload)        
        response.raise_for_status()
        data = response.json()
        print(f"Job submitted successfully! Job ID: {data['job_id']}")
    except Exception as e:
        print(f"Error submitting job: {e}")

def status_job(args):
    wait = getattr(args, "wait", False)
    timeout = 300  # seconds, i.e. 5 minutes max wait
    poll_interval = 5  # seconds between polls
    start_time = time.time()

    while True:
        try:
            response = requests.get(f"{BACKEND_URL}/status/{args.job_id}")
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                print(f"Error: {data['error']}")
                return

            status = data.get("status", "unknown")
            print(f"Job ID: {data['job_id']} - Status: {status}")

            if not wait or status in ("success", "failed"):
                print("Job details:")
                for k, v in data.get("job", {}).items():
                    print(f"  {k}: {v}")
                break

            if time.time() - start_time > timeout:
                print("Timeout reached while waiting for job to finish.")
                break

            print(f"Waiting {poll_interval}s before next status check...")
            time.sleep(poll_interval)

        except Exception as e:
            print(f"Error getting status: {e}")
            break

def main():
    parser = argparse.ArgumentParser(prog="qgjob", description="QualGent Test Job CLI")
    subparsers = parser.add_subparsers(help="commands")

    # Submit command
    parser_submit = subparsers.add_parser("submit", help="Submit a new test job")  
    parser_submit.add_argument("--org-id", required=True)
    parser_submit.add_argument("--app-version-id", required=True)
    parser_submit.add_argument("--test", required=True)
    parser_submit.add_argument("--priority", type=int, default=1)
    parser_submit.add_argument("--target", required=True, choices=["emulator", "device", "browserstack"])
    parser_submit.set_defaults(func=submit_job)

    # Status command
    parser_status = subparsers.add_parser("status", help="Get status of a job by job ID")
    parser_status.add_argument("--job-id", required=True)
    parser_status.add_argument("--wait", action="store_true", help="Wait for job to complete (poll status)")
    parser_status.set_defaults(func=status_job)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()