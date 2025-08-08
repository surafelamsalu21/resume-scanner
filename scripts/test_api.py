#!/usr/bin/env python3
"""
Simple script to test the Resume AI Backend API endpoints.
This can be used for quick manual testing of the API.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BASE_URL = os.environ.get('API_URL', 'http://localhost:5000')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'your-password')

# Colors for terminal output


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_response(response, label=None):
    """Print formatted API response"""
    if label:
        print(f"\n{Colors.BOLD}{label}{Colors.ENDC}")

    print(f"{Colors.OKBLUE}Status Code:{Colors.ENDC} {response.status_code}")
    print(f"{Colors.OKBLUE}Headers:{Colors.ENDC}")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")

    print(f"{Colors.OKBLUE}Response Body:{Colors.ENDC}")
    try:
        formatted_json = json.dumps(response.json(), indent=2)
        print(formatted_json)
    except:
        print(response.text)

    print("\n" + "-"*80)


def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")
    return response.status_code == 200


def get_admin_token():
    """Get admin authentication token"""
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }

    response = requests.post(f"{BASE_URL}/admin/login", json=login_data)
    print_response(response, "Admin Login")

    if response.status_code == 200:
        return response.json().get('access_token')
    return None


def test_admin_endpoints(token):
    """Test admin endpoints with authentication"""
    if not token:
        print(
            f"{Colors.FAIL}No admin token available. Skipping admin tests.{Colors.ENDC}")
        return False

    headers = {"Authorization": f"Bearer {token}"}

    # Test getting jobs
    response = requests.get(f"{BASE_URL}/admin/jobs", headers=headers)
    print_response(response, "Admin Jobs")

    # Test analytics
    response = requests.get(f"{BASE_URL}/admin/analytics", headers=headers)
    print_response(response, "Admin Analytics")

    return True


def test_resume_upload(token=None):
    """Test resume upload endpoint"""
    # This is a placeholder - you would need an actual resume file to test
    print(f"{Colors.WARNING}Resume upload test requires a file. Skipping for now.{Colors.ENDC}")
    print(f"{Colors.WARNING}To test manually, use: curl -F 'file=@path/to/resume.pdf' -F 'job_role=software_engineer' {BASE_URL}/api/resume/upload{Colors.ENDC}")
    return True


def main():
    """Main test function"""
    print(f"{Colors.HEADER}Testing Resume AI Backend API at {BASE_URL}{Colors.ENDC}")
    print("-"*80)

    # Test health check
    health_ok = test_health_check()
    if not health_ok:
        print(f"{Colors.FAIL}Health check failed. Exiting tests.{Colors.ENDC}")
        sys.exit(1)

    # Get admin token
    token = get_admin_token()

    # Test admin endpoints
    admin_ok = test_admin_endpoints(token)

    # Test resume upload
    upload_ok = test_resume_upload(token)

    # Summary
    print(f"\n{Colors.HEADER}Test Summary:{Colors.ENDC}")
    print(f"Health Check: {'✅' if health_ok else '❌'}")
    print(f"Admin Endpoints: {'✅' if admin_ok else '❌'}")
    print(
        f"Resume Upload: {'⚠️ (Manual testing required)' if upload_ok else '❌'}")

    print(f"\n{Colors.BOLD}For complete API testing, run:{Colors.ENDC}")
    print("pytest")


if __name__ == "__main__":
    main()
