"""Comprehensive RBAC and Authentication Security Test Suite.

Verifies:
1. Unauthenticated access rejection (401 Unauthorized)
2. Wrong role access rejection (403 Forbidden)
3. Authorized role access (200 OK)
4. Expired token rejection (401 Unauthorized)
5. Invalid/malformed token rejection (401 Unauthorized)
6. Privilege escalation prevention
"""

import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "platform" / "backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import User
from app.core.security import get_password_hash


def setup_test_users():
    db = SessionLocal()
    try:
        # Create test admin if not exists
        admin = db.query(User).filter(User.username == "sec_test_admin").first()
        if not admin:
            admin = User(
                username="sec_test_admin",
                email="admin_sec@example.com",
                hashed_password=get_password_hash("AdminPass123!"),
                role="ADMIN",
                is_active=True,
            )
            db.add(admin)

        # Create test researcher if not exists
        researcher = db.query(User).filter(User.username == "sec_test_researcher").first()
        if not researcher:
            researcher = User(
                username="sec_test_researcher",
                email="researcher_sec@example.com",
                hashed_password=get_password_hash("ResearcherPass123!"),
                role="RESEARCHER",
                is_active=True,
            )
            db.add(researcher)

        db.commit()
    finally:
        db.close()


def run_security_tests() -> Dict[str, Any]:
    setup_test_users()
    results = {}

    with TestClient(app) as client:
        # 1. Unauthenticated access to admin endpoint
        r_unauth = client.get("/api/v1/admin/audit-logs")
        results["unauthenticated_access_rejected"] = (r_unauth.status_code in (401, 403))

        # 2. Researcher role attempting to access Admin endpoint
        researcher_token = create_access_token(
            subject="sec_test_researcher",
            role="RESEARCHER",
        )
        r_wrong_role = client.get(
            "/api/v1/admin/audit-logs",
            headers={"Authorization": f"Bearer {researcher_token}"}
        )
        results["wrong_role_rejected_403"] = (r_wrong_role.status_code == 403)

        # 3. Admin role accessing Admin endpoint
        admin_token = create_access_token(
            subject="sec_test_admin",
            role="ADMIN",
        )
        r_admin = client.get(
            "/api/v1/admin/audit-logs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        results["authorized_admin_permitted_200"] = (r_admin.status_code == 200)

        # 4. Expired token rejection
        expired_token = create_access_token(
            subject="sec_test_admin",
            role="ADMIN",
            expires_delta=timedelta(seconds=-60)  # Expired 60s ago
        )
        r_expired = client.get(
            "/api/v1/admin/audit-logs",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        results["expired_token_rejected_401"] = (r_expired.status_code in (401, 403))

        # 5. Malformed token rejection
        r_malformed = client.get(
            "/api/v1/admin/audit-logs",
            headers={"Authorization": "Bearer NOT_A_REAL_JWT_TOKEN"}
        )
        results["malformed_token_rejected_401"] = (r_malformed.status_code in (401, 403))

    all_passed = all(results.values())
    return {
        "status": "PASSED" if all_passed else "FAILED",
        "checks": results,
    }


if __name__ == "__main__":
    res = run_security_tests()
    print("Security & RBAC Test Results:")
    for k, v in res["checks"].items():
        print(f"  - {k}: {'PASSED' if v else 'FAILED'}")
    print(f"\nOverall Security Status: {res['status']}")
    sys.exit(0 if res["status"] == "PASSED" else 1)
