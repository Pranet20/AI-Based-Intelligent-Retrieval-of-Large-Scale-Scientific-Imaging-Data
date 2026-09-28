from pathlib import Path
import numpy as np
from PIL import Image
import pytest

from app.ml.duplicate_engine import DuplicateEngine


@pytest.fixture
def duplicate_pair(tmp_path):
    p1 = tmp_path / "img1.png"
    p2 = tmp_path / "img2.png"
    arr = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
    Image.fromarray(arr).save(p1)
    Image.fromarray(arr).save(p2)
    return p1, p2


def test_exact_duplicate_detection(duplicate_pair):
    p1, p2 = duplicate_pair
    h1 = DuplicateEngine.compute_hashes(p1)
    h2 = DuplicateEngine.compute_hashes(p2)

    assert h1["sha256"] == h2["sha256"]
    assert h1["phash"] == h2["phash"]
    assert h1["dhash"] == h2["dhash"]

    candidate = {
        "id": 1,
        "storage_path": str(p1),
        "sha256": h1["sha256"],
        "phash": h1["phash"],
        "dhash": h1["dhash"],
        "dinov2_vector": np.ones(384, dtype=np.float32) / np.sqrt(384),
        "adapted_vector": np.ones(384, dtype=np.float32) / np.sqrt(384),
    }

    res = DuplicateEngine.check_duplicate_against_candidates(
        new_image_path=p2,
        new_sha256=h2["sha256"],
        new_phash=h2["phash"],
        new_dhash=h2["dhash"],
        new_dinov2_vec=candidate["dinov2_vector"],
        new_adapted_vec=candidate["adapted_vector"],
        candidates=[candidate],
    )

    assert res["duplicate_status"] == "EXACT_DUPLICATE"
    assert res["matched_image_id"] == 1
    assert res["similarity_score"] == 1.0
