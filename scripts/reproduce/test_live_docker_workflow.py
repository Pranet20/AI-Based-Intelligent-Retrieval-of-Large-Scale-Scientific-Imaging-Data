"""Full end-to-end integration and smoke test against the live running Docker stack."""

import sys
from pathlib import Path
import httpx

BASE_URL = "http://localhost:8000/api/v1"
NGINX_URL = "http://localhost:3000/api/v1"

def run_live_workflow_test():
    print(f"=== Testing Live Scientific Platform Workflow against Docker ===")
    client = httpx.Client(timeout=30.0)

    # 1. Healthcheck direct and via Nginx proxy
    res_direct = client.get(f"{BASE_URL}/health")
    assert res_direct.status_code == 200, f"Direct healthcheck failed: {res_direct.text}"
    print(f"[PASS] Direct Backend Health: {res_direct.json()}")

    res_proxy = client.get(f"{NGINX_URL}/health")
    assert res_proxy.status_code == 200, f"Nginx reverse-proxy healthcheck failed: {res_proxy.text}"
    print(f"[PASS] Nginx Reverse-Proxy Health: {res_proxy.json()}")

    # 2. Readiness check
    res_readiness = client.get(f"{BASE_URL}/readiness")
    assert res_readiness.status_code == 200, f"Readiness check failed: {res_readiness.text}"
    print(f"[PASS] System Readiness: {res_readiness.json()}")

    # 3. Authentication
    login_data = {"username": "admin", "password": "adminpassword123"}
    res_login = client.post(f"{BASE_URL}/auth/login", data=login_data)
    if res_login.status_code != 200:
        # Register if not yet registered
        reg_data = {
            "username": "admin",
            "email": "admin@scidata.internal",
            "password": "adminpassword123",
            "role": "ADMIN"
        }
        res_reg = client.post(f"{BASE_URL}/auth/register", json=reg_data)
        assert res_reg.status_code == 200, f"Admin registration failed: {res_reg.text}"
        res_login = client.post(f"{BASE_URL}/auth/login", data=login_data)

    token = res_login.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    print(f"[PASS] Authentication & JWT Generation succeeded (role: {res_login.json()['role']})")

    # 4. Project Creation
    proj_payload = {
        "name": "Live Micrograph Benchmark Suite",
        "description": "Validation dataset of high-resolution scanning electron micrographs"
    }
    res_proj = client.post(f"{BASE_URL}/projects", json=proj_payload, headers=auth_headers)
    assert res_proj.status_code == 200, f"Project creation failed: {res_proj.text}"
    project_id = res_proj.json()["id"]
    print(f"[PASS] Created Benchmark Project: ID={project_id}, Name='{res_proj.json()['name']}'")

    # 5. Image Ingestion
    sample_img_path = Path("data/raw/hcci/Images/1.png")
    if not sample_img_path.exists():
        print("[WARN] Sample image 1.png not found, creating synthetic micrograph for upload test")
        sample_img_path = Path("platform/storage/synthetic_test_micrograph.png")
        from PIL import Image as PILImage
        import numpy as np
        img = PILImage.fromarray((np.random.rand(256, 256) * 255).astype(np.uint8))
        img.save(sample_img_path)

    with open(sample_img_path, "rb") as f:
        upload_files = {"file": ("hcci_micrograph_001.png", f.read(), "image/png")}
    upload_data = {
        "project_id": str(project_id),
        "microscope": "FEI Helios Nanolab 600",
        "detector": "TLD",
        "accelerating_voltage_kv": "5.0",
        "magnification": "25000.0",
        "pixel_size_nm": "4.2",
    }
    res_upload = client.post(
        f"{BASE_URL}/images/upload",
        files=upload_files,
        data=upload_data,
        headers=auth_headers,
    )
    # 400 is possible if already uploaded due to unique SHA-256 idempotency check!
    if res_upload.status_code == 400 and "already exists" in res_upload.text:
        print("[PASS] SHA-256 Idempotency: Image already uploaded in previous test.")
        # Retrieve existing image
        images_list = client.get(f"{BASE_URL}/images?project_id={project_id}", headers=auth_headers).json()
        image_id = images_list["items"][0]["id"]
    else:
        assert res_upload.status_code == 200, f"Image upload failed: {res_upload.text}"
        image_id = res_upload.json()["id"]
        print(f"[PASS] Image Ingestion & Analysis completed: ID={image_id}, SHA256={res_upload.json()['sha256'][:16]}...")

    # 6. Image Detail Query
    res_detail = client.get(f"{BASE_URL}/images/{image_id}", headers=auth_headers)
    assert res_detail.status_code == 200, f"Image detail failed: {res_detail.text}"
    detail = res_detail.json()
    print(f"[PASS] Image Detail Verified: status={detail['processing_status']}, quality={detail['quality']['quality_label']}, dup={detail['duplicate']['duplicate_status']}")

    # 7. Similarity Search
    search_data = {
        "image_id": str(image_id),
        "top_k": "5",
    }
    res_search = client.post(f"{BASE_URL}/search/vector", data=search_data, headers=auth_headers)
    assert res_search.status_code == 200, f"Search failed: {res_search.text}"
    search_res = res_search.json()
    print(f"[PASS] Vector Retrieval executed: query_mode='{search_res.get('query_mode')}', results count={len(search_res.get('results', []))}")

    # 8. Curation & Review Queue
    res_queue = client.get(f"{BASE_URL}/curation/review-queue", headers=auth_headers)
    assert res_queue.status_code == 200, f"Review queue query failed: {res_queue.text}"
    queue_items = res_queue.json()
    print(f"[PASS] Curation Review Queue: {len(queue_items)} items pending review")

    # Submit a curation review decision
    review_body = {
        "image_id": image_id,
        "decision": "KEEP",
        "comment": "Verified nominal micrograph quality and metadata integrity during final Docker smoke test."
    }
    res_review = client.post(f"{BASE_URL}/curation/reviews", json=review_body, headers=auth_headers)
    assert res_review.status_code == 200, f"Curation decision failed: {res_review.text}"
    print(f"[PASS] Curator Review Decision Recorded: ID={res_review.json()['review_id']}, decision='{res_review.json()['decision']}'")

    print("\n=== ALL LIVE DOCKER RUNTIME WORKFLOW TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    try:
        run_live_workflow_test()
    except Exception as e:
        print(f"\n[FAIL] Workflow test encountered error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
