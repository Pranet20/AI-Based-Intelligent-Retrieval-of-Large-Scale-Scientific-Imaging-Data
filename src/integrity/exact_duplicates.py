"""
Track A: Exact Duplicate Detection (Bitwise File Hash and Decoded Pixel Buffer Hash).

Distinguishes:
1. Exact container/file duplicates (identical bytes on disk).
2. Exact decoded pixel duplicates (identical visual pixel array even if metadata/headers differ).
"""

import hashlib
from pathlib import Path
from typing import Dict, List, Union, Tuple
import numpy as np
from PIL import Image
import pandas as pd


def compute_file_sha256(file_path: Union[str, Path], chunk_size: int = 65536) -> str:
    """Compute the SHA-256 hexadecimal hash of raw file bytes on disk."""
    p = Path(file_path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")
    hasher = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_decoded_pixel_sha256(
    image_input: Union[str, Path, np.ndarray, Image.Image],
    target_mode: str = "L",
) -> str:
    """
    Compute SHA-256 hash of decoded raw uncompressed pixel buffer.

    Parameters
    ----------
    image_input : path, np.ndarray, or PIL Image.
    target_mode : 'L' for 8-bit grayscale, 'RGB' for 24-bit RGB.
                  Standardizes color space representation across formats.

    Returns
    -------
    Hexadecimal string of SHA-256 hash of raw contiguous C-ordered bytes.
    """
    if isinstance(image_input, (str, Path)):
        img = Image.open(image_input)
    elif isinstance(image_input, Image.Image):
        img = image_input
    elif isinstance(image_input, np.ndarray):
        img = Image.fromarray(image_input)
    else:
        raise TypeError(f"Unsupported image input type: {type(image_input)}")

    # Convert to standardized mode
    if img.mode != target_mode:
        img = img.convert(target_mode)

    arr = np.ascontiguousarray(np.array(img, dtype=np.uint8))
    hasher = hashlib.sha256()
    hasher.update(arr.tobytes())
    return hasher.hexdigest()


def find_exact_file_duplicates(
    manifest_df: pd.DataFrame,
    path_col: str = "file_path",
    id_col: str = "image_id",
) -> Dict[str, List[str]]:
    """
    Find clusters of exact file bitwise duplicates.

    Returns
    -------
    dict mapping hash -> list of image_ids with that identical hash (size > 1)
    """
    hash_to_ids: Dict[str, List[str]] = {}
    for _, row in manifest_df.iterrows():
        img_id = str(row[id_col])
        fpath = row[path_col]
        h = compute_file_sha256(fpath)
        hash_to_ids.setdefault(h, []).append(img_id)

    return {h: ids for h, ids in hash_to_ids.items() if len(ids) > 1}


def find_exact_pixel_duplicates(
    manifest_df: pd.DataFrame,
    path_col: str = "file_path",
    id_col: str = "image_id",
    target_mode: str = "L",
) -> Dict[str, List[str]]:
    """
    Find clusters of exact decoded pixel buffer duplicates.

    Returns
    -------
    dict mapping hash -> list of image_ids with identical decoded pixels (size > 1)
    """
    hash_to_ids: Dict[str, List[str]] = {}
    for _, row in manifest_df.iterrows():
        img_id = str(row[id_col])
        fpath = row[path_col]
        h = compute_decoded_pixel_sha256(fpath, target_mode=target_mode)
        hash_to_ids.setdefault(h, []).append(img_id)

    return {h: ids for h, ids in hash_to_ids.items() if len(ids) > 1}
