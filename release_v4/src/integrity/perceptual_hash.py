"""
Track A: Perceptual Hashing (64-bit pHash and dHash).

Provides fast perceptual fingerprinting for near-duplicate candidate filtering:
- pHash: 2D Discrete Cosine Transform (DCT) based frequency hash.
- dHash: Directional gradient difference hash.
"""

from pathlib import Path
from typing import Union, List, Tuple
import numpy as np
from PIL import Image
import scipy.fft


def _load_gray_image(image_input: Union[str, Path, np.ndarray, Image.Image]) -> Image.Image:
    """Helper to load image as PIL Grayscale ('L')."""
    if isinstance(image_input, (str, Path)):
        img = Image.open(image_input)
    elif isinstance(image_input, Image.Image):
        img = image_input
    elif isinstance(image_input, np.ndarray):
        img = Image.fromarray(image_input)
    else:
        raise TypeError(f"Unsupported image input type: {type(image_input)}")
    if img.mode != "L":
        img = img.convert("L")
    return img


def compute_phash(
    image_input: Union[str, Path, np.ndarray, Image.Image],
    hash_size: int = 8,
    highfreq_factor: int = 4,
) -> np.ndarray:
    """
    Compute 2D DCT-based perceptual hash (pHash).

    Parameters
    ----------
    image_input : path, PIL Image, or ndarray.
    hash_size : size of the square hash block (default 8 -> 64 bits).
    highfreq_factor : resize multiplier for DCT calculation (default 4 -> 32x32).

    Returns
    -------
    np.ndarray of bool with shape (hash_size * hash_size,) = (64,)
    """
    img = _load_gray_image(image_input)
    img_size = hash_size * highfreq_factor
    # Bilinear or Lanczos resize
    resized = img.resize((img_size, img_size), Image.Resampling.BILINEAR)
    pixels = np.asarray(resized, dtype=np.float32)

    # 2D DCT (ortho normalized)
    dct = scipy.fft.dct(scipy.fft.dct(pixels, axis=0, norm="ortho"), axis=1, norm="ortho")

    # Extract low frequency top-left block
    dct_low = dct[:hash_size, :hash_size]

    # Median excluding DC term (0, 0)
    med = np.median(dct_low[1:, 1:])
    diff = dct_low > med
    return diff.flatten()


def compute_dhash(
    image_input: Union[str, Path, np.ndarray, Image.Image],
    hash_size: int = 8,
) -> np.ndarray:
    """
    Compute difference hash (dHash) tracking horizontal intensity gradients.

    Parameters
    ----------
    image_input : path, PIL Image, or ndarray.
    hash_size : width/height of hash block (default 8 -> (hash_size+1, hash_size) -> 64 bits).

    Returns
    -------
    np.ndarray of bool with shape (hash_size * hash_size,) = (64,)
    """
    img = _load_gray_image(image_input)
    # Resize to (width = hash_size + 1, height = hash_size)
    resized = img.resize((hash_size + 1, hash_size), Image.Resampling.BILINEAR)
    pixels = np.asarray(resized, dtype=np.float32)

    # Compare adjacent pixels horizontally: col[x+1] > col[x]
    diff = pixels[:, 1:] > pixels[:, :-1]
    return diff.flatten()


def hash_to_hex(hash_bits: np.ndarray) -> str:
    """Convert boolean hash array (64 bits) to 16-character hexadecimal string."""
    flat = hash_bits.astype(np.uint8)
    byte_arr = np.packbits(flat)
    return byte_arr.tobytes().hex()


def hex_to_hash(hex_str: str) -> np.ndarray:
    """Convert hexadecimal string back to boolean hash array."""
    byte_arr = bytes.fromhex(hex_str)
    bits = np.unpackbits(np.frombuffer(byte_arr, dtype=np.uint8))
    return bits.astype(bool)


def hamming_distance(hash1: np.ndarray, hash2: np.ndarray) -> int:
    """Compute Hamming distance (count of bit differences) between two boolean hash vectors."""
    return int(np.count_nonzero(hash1 != hash2))


def pairwise_hamming_matrix(hashes: np.ndarray) -> np.ndarray:
    """
    Compute all-pairs Hamming distances for a matrix of boolean hashes of shape (N, B).

    Parameters
    ----------
    hashes : bool ndarray of shape (N, B) where B is number of bits (e.g. 64).

    Returns
    -------
    ndarray of shape (N, N) with integer Hamming distances.
    """
    N, B = hashes.shape
    # XOR via !=, sum across bits axis
    # For moderate N (e.g., 774): (N, 1, B) != (1, N, B) is 774x774x64 ~ 38MB RAM
    diffs = hashes[:, None, :] != hashes[None, :, :]
    return np.sum(diffs, axis=2, dtype=np.int32)
