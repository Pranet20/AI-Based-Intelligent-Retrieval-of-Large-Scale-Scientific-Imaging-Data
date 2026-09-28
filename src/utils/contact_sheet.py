"""Deterministic sample image contact sheet generator."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.ingestion.reader import ScientificImageReader


def generate_contact_sheet(
    image_records: List[Dict[str, Any]],
    output_path: str | Path,
    dataset_id: str,
    max_images: int = 16,
    grid_cols: int = 4,
    thumb_size: int = 256,
    seed: int = 42,
) -> Path:
    """Generate a deterministic contact sheet for a sample of images.

    Important scientific disclaimer:
    Deterministic pseudo-random sampling is employed here for visual quality inspection
    and should not be claimed as statistically representative without formal sampling design.
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    if not image_records:
        raise ValueError("Cannot generate contact sheet from empty image records.")

    # Deterministic sampling
    rng = np.random.RandomState(seed)
    n = min(len(image_records), max_images)
    indices = sorted(rng.choice(len(image_records), size=n, replace=False))
    selected = [image_records[i] for i in indices]

    grid_rows = math.ceil(n / grid_cols)
    header_height = 50
    caption_height = 40
    cell_w = thumb_size
    cell_h = thumb_size + caption_height

    sheet_w = grid_cols * cell_w
    sheet_h = header_height + grid_rows * cell_h

    # Create white canvas
    sheet = Image.new("RGB", (sheet_w, sheet_h), color=(255, 255, 255))
    draw = ImageDraw.Draw(sheet)

    # Title Banner
    banner_text = f"Dataset: {dataset_id} | Sample Inspection Sheet (N={n}, Seed={seed})"
    draw.rectangle([(0, 0), (sheet_w, header_height)], fill=(30, 41, 59))
    draw.text((15, 15), banner_text, fill=(255, 255, 255))

    for idx, rec in enumerate(selected):
        r = idx // grid_cols
        c = idx % grid_cols
        x = c * cell_w
        y = header_height + r * cell_h

        img_path = rec.get("absolute_path_if_local_only") or rec.get("file_path")
        thumb_img = None
        if img_path and Path(img_path).is_file():
            try:
                arr, _ = ScientificImageReader.load_array(img_path)
                # Normalize for display
                if arr.dtype != np.uint8:
                    min_v, max_v = float(np.min(arr)), float(np.max(arr))
                    if max_v > min_v:
                        arr_norm = ((arr - min_v) / (max_v - min_v) * 255.0).astype(np.uint8)
                    else:
                        arr_norm = np.zeros_like(arr, dtype=np.uint8)
                else:
                    arr_norm = arr

                if arr_norm.ndim == 2:
                    pil_img = Image.fromarray(arr_norm, mode="L").convert("RGB")
                elif arr_norm.ndim == 3:
                    pil_img = Image.fromarray(arr_norm)
                else:
                    pil_img = Image.new("RGB", (thumb_size, thumb_size), color=(128, 128, 128))

                pil_img.thumbnail((thumb_size, thumb_size), Image.Resampling.LANCZOS)
                thumb_img = pil_img
            except Exception:
                pass

        if thumb_img is None:
            thumb_img = Image.new("RGB", (thumb_size, thumb_size), color=(200, 200, 200))
            d_box = ImageDraw.Draw(thumb_img)
            d_box.text((10, thumb_size // 2), "Unreadable", fill=(0, 0, 0))

        # Center thumbnail in cell
        offset_x = x + (thumb_size - thumb_img.width) // 2
        offset_y = y + (thumb_size - thumb_img.height) // 2
        sheet.paste(thumb_img, (offset_x, offset_y))

        # Caption
        img_id = str(rec.get("image_id", ""))[:18]
        fname = str(rec.get("filename", ""))[:20]
        caption = f"ID: {img_id}\nFile: {fname}"
        draw.text((x + 6, y + thumb_size + 4), caption, fill=(51, 65, 85))

        # Cell border
        draw.rectangle([(x, y), (x + cell_w - 1, y + cell_h - 1)], outline=(226, 232, 240))

    sheet.save(out, format="JPEG", quality=90)
    return out
