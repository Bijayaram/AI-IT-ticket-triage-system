"""
Fine-tune BAAI/bge-m3 on IT ticket data using contrastive learning.

Strategy:
  - Tickets from the same department form positive pairs.
  - MultipleNegativesRankingLoss (in-batch negatives) via manual training loop.
  - Freeze all but the last 2 transformer layers for CPU speed + less overfitting.
  - Subsample pairs so training finishes in a reasonable time on CPU.

Uses a manual PyTorch loop to avoid Trainer API version-compatibility issues.
"""
import sys
import os
import random
import time
import logging
from pathlib import Path
from collections import defaultdict

import pandas as pd
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset as TorchDataset

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def log(msg: str):
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DATASET_PATH_DEFAULT = r"D:\Capstone\Dataset\aa_dataset-tickets-multi-lang-5-2-50-version.csv"
OUTPUT_DIR = "./models/bge-m3-finetuned"
MAX_PAIRS = 1500
BATCH_SIZE = 8
EPOCHS = 1
LR = 2e-5
MAX_SEQ_LEN = 256
SEED = 42
FREEZE_BELOW_LAYER = 22  # bge-m3 has 24 layers (0-23); train only 22 & 23

QUEUE_MAPPING = {
    "General Inquiry": "Customer Service",
    "Human Resources": "Customer Service",
    "IT Support": "Technical Support",
    "Returns and Exchanges": "Product Support",
    "Sales and Pre-Sales": "Product Support",
}


# ---------------------------------------------------------------------------
# Pair dataset
# ---------------------------------------------------------------------------
class PairDataset(TorchDataset):
    def __init__(self, anchors: list[str], positives: list[str]):
        self.anchors = anchors
        self.positives = positives

    def __len__(self):
        return len(self.anchors)

    def __getitem__(self, idx):
        return self.anchors[idx], self.positives[idx]


# ---------------------------------------------------------------------------
# Multiple Negatives Ranking Loss (manual)
# ---------------------------------------------------------------------------
def mnrl_loss(anchor_emb: torch.Tensor, positive_emb: torch.Tensor, scale: float = 20.0):
    """
    In-batch negatives: each anchor should be closest to its own positive.
    similarity matrix is (batch, batch); labels = diagonal.
    """
    scores = torch.mm(anchor_emb, positive_emb.t()) * scale
    labels = torch.arange(scores.size(0), device=scores.device)
    return torch.nn.functional.cross_entropy(scores, labels)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def freeze_lower_layers(model):
    trainable, frozen = 0, 0
    for name, param in model.named_parameters():
        should_train = False
        if "encoder.layer." in name:
            layer_idx = int(name.split("encoder.layer.")[1].split(".")[0])
            if layer_idx >= FREEZE_BELOW_LAYER:
                should_train = True
        if "pooler" in name:
            should_train = True

        param.requires_grad = should_train
        if should_train:
            trainable += param.numel()
        else:
            frozen += param.numel()

    pct = trainable / (trainable + frozen) * 100
    log(f"       Trainable: {trainable:,} ({pct:.1f}%)  Frozen: {frozen:,}")


def build_pairs(df: pd.DataFrame, max_pairs: int):
    by_dept: dict[str, list[str]] = defaultdict(list)
    for _, row in df.iterrows():
        by_dept[row["queue"]].append(row["text"])

    anchors, positives = [], []
    per_dept = max(max_pairs // len(by_dept), 50)
    for dept, texts in by_dept.items():
        n = len(texts)
        for _ in range(min(per_dept, n)):
            i, j = random.sample(range(n), 2)
            anchors.append(texts[i])
            positives.append(texts[j])

    combined = list(zip(anchors, positives))
    random.shuffle(combined)
    combined = combined[:max_pairs]
    return [a for a, _ in combined], [p for _, p in combined]


def encode_batch(model, tokenizer, texts: list[str], device: torch.device) -> torch.Tensor:
    """Tokenize + forward through the transformer, return normalized CLS embeddings."""
    encoded = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=MAX_SEQ_LEN,
        return_tensors="pt",
    ).to(device)
    outputs = model[0].auto_model(**encoded)
    emb = outputs.last_hidden_state[:, 0]
    emb = torch.nn.functional.normalize(emb, p=2, dim=1)
    return emb


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    from sentence_transformers import SentenceTransformer

    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)

    dataset_path = sys.argv[1] if len(sys.argv) > 1 else DATASET_PATH_DEFAULT
    device = torch.device("cpu")

    log("\n" + "=" * 80)
    log("  FINE-TUNING BAAI/bge-m3 ON IT TICKET DATA (contrastive learning)")
    log("=" * 80)

    # --- 1. Load data --------------------------------------------------------
    log(f"\n[1/6] Loading dataset: {dataset_path}")
    df = pd.read_csv(dataset_path)
    df["text"] = df["subject"].fillna("") + "\n\n" + df["body"].fillna("")
    df = df[df["queue"].notna() & df["text"].notna()].copy()
    df["queue"] = df["queue"].replace(QUEUE_MAPPING)
    log(f"       {len(df)} tickets, {df['queue'].nunique()} departments")

    # --- 2. Build contrastive pairs ------------------------------------------
    log(f"\n[2/6] Building contrastive pairs (same dept = positive) ...")
    anchors, positives = build_pairs(df, MAX_PAIRS)
    log(f"       {len(anchors)} training pairs")
    dataset = PairDataset(anchors, positives)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, drop_last=True)

    # --- 3. Load model -------------------------------------------------------
    log(f"\n[3/6] Loading BAAI/bge-m3 ...")
    model = SentenceTransformer("BAAI/bge-m3")
    model.max_seq_length = MAX_SEQ_LEN
    tokenizer = model.tokenizer
    log(f"       Embedding dim: {model.get_sentence_embedding_dimension()}")

    # --- 4. Freeze lower layers ----------------------------------------------
    log(f"\n[4/6] Freezing layers 0-{FREEZE_BELOW_LAYER - 1} (training {FREEZE_BELOW_LAYER}-23 + pooler)")
    freeze_lower_layers(model)

    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable_params, lr=LR, weight_decay=0.01)
    n_steps = len(loader)

    warmup_steps = max(1, int(0.1 * n_steps))
    scheduler = torch.optim.lr_scheduler.LinearLR(
        optimizer, start_factor=0.1, total_iters=warmup_steps
    )

    # --- 5. Train ------------------------------------------------------------
    log(f"\n[5/6] Training: {n_steps} steps, batch={BATCH_SIZE}, lr={LR}")

    model.train()
    start = time.time()

    for epoch in range(EPOCHS):
        total_loss = 0.0
        for step, (anchor_texts, positive_texts) in enumerate(loader, 1):
            optimizer.zero_grad()

            anchor_emb = encode_batch(model, tokenizer, list(anchor_texts), device)
            positive_emb = encode_batch(model, tokenizer, list(positive_texts), device)

            loss = mnrl_loss(anchor_emb, positive_emb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=1.0)
            optimizer.step()
            if step <= warmup_steps:
                scheduler.step()

            total_loss += loss.item()

            if step % 5 == 0 or step == 1 or step == n_steps:
                elapsed_so_far = time.time() - start
                avg_loss = total_loss / step
                secs_per_step = elapsed_so_far / step
                remaining = secs_per_step * (n_steps - step)
                log(
                    f"  step {step:>4d}/{n_steps}  "
                    f"loss={loss.item():.4f}  avg={avg_loss:.4f}  "
                    f"({elapsed_so_far / 60:.1f}m elapsed, ~{remaining / 60:.0f}m left)"
                )

        log(f"  Epoch {epoch + 1} done -- avg loss: {total_loss / n_steps:.4f}")

    elapsed = time.time() - start

    # --- 6. Save fine-tuned model -------------------------------------------
    log(f"\n[6/6] Saving fine-tuned model to {OUTPUT_DIR}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model.save(OUTPUT_DIR)

    log(f"\n  Fine-tuning done in {elapsed / 60:.1f} minutes")

    # --- 7. Generate & cache new embeddings while model is in memory --------
    log(f"\n[BONUS] Generating dataset embeddings with fine-tuned model ...")
    log(f"        (avoids reloading the 2.3 GB model from disk)")
    model.eval()
    all_texts = df["text"].tolist()
    batch = 32
    from backend.ml.embeddings import LocalEmbedder
    cache_dir = Path(LocalEmbedder.CACHE_DIR)
    cache_dir.mkdir(exist_ok=True)

    import pickle
    embeddings = model.encode(
        all_texts,
        batch_size=batch,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    cache_path = cache_dir / "dataset_embeddings.pkl"
    with open(cache_path, "wb") as f:
        pickle.dump(embeddings, f)
    log(f"        Cached {embeddings.shape} embeddings to {cache_path}")

    log(f"\n{'=' * 80}")
    log(f"  ALL DONE  --  model saved + embeddings cached")
    log(f"  Model: {os.path.abspath(OUTPUT_DIR)}")
    log(f"  Embeddings: {cache_path}")
    log(f"{'=' * 80}\n")


if __name__ == "__main__":
    sys.exit(main() or 0)
