"""
Generate embeddings using the fine-tuned bge-m3 model.

Approach: Load the original BAAI/bge-m3 (from HF cache), then patch in
the fine-tuned weights for layers 22-23 from the saved safetensors file.
This avoids loading the full 2.3 GB model from scratch and sidesteps
the Windows memory crash on reload.
"""
import sys
import os
import pickle
import time
import logging
from pathlib import Path

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def log(msg: str):
    print(msg, flush=True)


DATASET_PATH_DEFAULT = r"D:\Capstone\Dataset\aa_dataset-tickets-multi-lang-5-2-50-version.csv"
FINETUNED_DIR = "./models/bge-m3-finetuned"
CACHE_DIR = "./embeddings_cache"
CACHE_FILE = "dataset_embeddings.pkl"

QUEUE_MAPPING = {
    "General Inquiry": "Customer Service",
    "Human Resources": "Customer Service",
    "IT Support": "Technical Support",
    "Returns and Exchanges": "Product Support",
    "Sales and Pre-Sales": "Product Support",
}

FINETUNE_LAYER_START = 22  # we fine-tuned layers 22 & 23


def main():
    import torch
    from safetensors.torch import load_file
    from sentence_transformers import SentenceTransformer

    dataset_path = sys.argv[1] if len(sys.argv) > 1 else DATASET_PATH_DEFAULT

    log("\n" + "=" * 80)
    log("  GENERATE EMBEDDINGS WITH FINE-TUNED BGE-M3 WEIGHTS")
    log("=" * 80)

    # 1. Load the original model (from HuggingFace cache -- fast & reliable)
    log("\n[1/4] Loading original BAAI/bge-m3 from cache ...")
    model = SentenceTransformer("BAAI/bge-m3")
    log(f"       Loaded.  Embedding dim: {model.get_sentence_embedding_dimension()}")

    # 2. Patch in fine-tuned weights for layers 22-23
    log(f"\n[2/4] Patching fine-tuned weights (layers {FINETUNE_LAYER_START}-23) ...")
    safetensors_path = os.path.join(FINETUNED_DIR, "model.safetensors")
    ft_state = load_file(safetensors_path, device="cpu")

    current_state = model[0].auto_model.state_dict()
    patched = 0
    for key in current_state:
        if "encoder.layer." in key:
            layer_idx = int(key.split("encoder.layer.")[1].split(".")[0])
            if layer_idx >= FINETUNE_LAYER_START:
                st_key = key
                if st_key in ft_state:
                    current_state[key] = ft_state[st_key]
                    patched += 1
        if "pooler" in key and key in ft_state:
            current_state[key] = ft_state[key]
            patched += 1

    model[0].auto_model.load_state_dict(current_state)
    del ft_state
    log(f"       Patched {patched} parameter tensors")

    # 3. Load dataset
    log(f"\n[3/4] Loading dataset: {dataset_path}")
    df = pd.read_csv(dataset_path)
    df["text"] = df["subject"].fillna("") + "\n\n" + df["body"].fillna("")
    df = df[df["queue"].notna() & df["text"].notna()].copy()
    df["queue"] = df["queue"].replace(QUEUE_MAPPING)
    all_texts = df["text"].tolist()
    log(f"       {len(all_texts)} texts to embed")

    # 4. Generate embeddings
    log(f"\n[4/4] Encoding {len(all_texts)} texts (batch=32) ...")
    model.eval()
    start = time.time()
    embeddings = model.encode(
        all_texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    elapsed = time.time() - start
    log(f"       Done in {elapsed / 60:.1f} min  shape={embeddings.shape}")

    # Save to cache
    cache_dir = Path(CACHE_DIR)
    cache_dir.mkdir(exist_ok=True)
    cache_path = cache_dir / CACHE_FILE
    with open(cache_path, "wb") as f:
        pickle.dump(embeddings, f)
    log(f"       Cached to {cache_path}")

    log(f"\n{'=' * 80}")
    log(f"  EMBEDDINGS READY  --  {elapsed / 60:.1f} minutes")
    log(f"  {cache_path}  ({embeddings.shape})")
    log(f"{'=' * 80}\n")


if __name__ == "__main__":
    sys.exit(main() or 0)
