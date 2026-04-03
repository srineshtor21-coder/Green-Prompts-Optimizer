"""
GreenPromptsOptimizer: Model Training Script (Large Dataset Version)
Trains T5-small on the expanded ~3000 pair dataset.

Usage:
    python train_optimizer_v2.py

Output:
    models/prompt_optimizer/   (upload this folder to Hugging Face)
"""

import json
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import (
    T5Tokenizer,
    T5ForConditionalGeneration,
    get_linear_schedule_with_warmup,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG = {
    "model_name": "t5-small",
    "dataset_path": "data/training_dataset_10k.json",
    "output_path": "models/prompt_optimizer",
    "batch_size": 8,           # larger batches since we have more data
    "num_epochs": 20,          # fewer epochs needed with more data
    "learning_rate": 3e-4,
    "max_input_length": 256,
    "max_output_length": 64,
    "warmup_ratio": 0.06,
    "gradient_accumulation_steps": 2,
    "val_split": 0.1,
    "save_every_n_epochs": 5,
}

DATA_DIR = Path("data")
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

class PromptDataset(Dataset):
    def __init__(self, pairs, tokenizer, max_in, max_out):
        self.pairs = pairs
        self.tokenizer = tokenizer
        self.max_in = max_in
        self.max_out = max_out

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        item = self.pairs[idx]
        enc = self.tokenizer(
            f"optimize: {item['original']}",
            max_length=self.max_in,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        dec = self.tokenizer(
            item["optimized"],
            max_length=self.max_out,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        labels = dec["input_ids"].clone()
        labels[labels == self.tokenizer.pad_token_id] = -100
        return {
            "input_ids": enc["input_ids"].squeeze(),
            "attention_mask": enc["attention_mask"].squeeze(),
            "labels": labels.squeeze(),
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_data():
    path = CONFIG["dataset_path"]
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    pairs = raw["data"]
    np.random.seed(42)
    np.random.shuffle(pairs)
    n_val = int(len(pairs) * CONFIG["val_split"])
    return pairs[n_val:], pairs[:n_val]


def run_epoch(model, loader, optimizer, scheduler, training=True):
    model.train() if training else model.eval()
    total_loss = 0.0
    steps = 0

    ctx = torch.enable_grad() if training else torch.no_grad()
    with ctx:
        for step, batch in enumerate(loader):
            ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            out = model(input_ids=ids, attention_mask=mask, labels=labels)
            loss = out.loss

            if training:
                (loss / CONFIG["gradient_accumulation_steps"]).backward()
                if (step + 1) % CONFIG["gradient_accumulation_steps"] == 0:
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad()

            total_loss += loss.item()
            steps += 1

    return total_loss / max(steps, 1)


def test_examples(model, tokenizer):
    model.eval()
    examples = [
        "Can you please help me understand how neural networks work in a very detailed way?",
        "I'm struggling to figure out how to reverse a linked list in Python could you help me",
        "What is machine learning?",
        "I would really like to know about quantum computing and how it differs from classical computing",
        "Could you kindly explain the process of photosynthesis and why it matters for life on earth?",
        "How do I sort a list in Python?",
        "I need you to very thoroughly explain what Docker containers are and how they work",
    ]
    print("\n--- Sample outputs ---")
    for prompt in examples:
        ids = tokenizer.encode(
            f"optimize: {prompt}",
            return_tensors="pt",
            max_length=CONFIG["max_input_length"],
            truncation=True,
        ).to(device)
        with torch.no_grad():
            out = model.generate(ids, max_length=CONFIG["max_output_length"], num_beams=4, early_stopping=True)
        result = tokenizer.decode(out[0], skip_special_tokens=True)
        reduction = 100 * (1 - len(result.split()) / max(len(prompt.split()), 1))
        print(f"  IN  : {prompt[:75]}")
        print(f"  OUT : {result}  ({reduction:.0f}% shorter)")
        print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 65)
    print("GreenPromptsOptimizer: Training v2 (Large Dataset)")
    print("=" * 65)

    train_pairs, val_pairs = load_data()
    print(f"Train: {len(train_pairs)}  |  Val: {len(val_pairs)}")

    tokenizer = T5Tokenizer.from_pretrained(CONFIG["model_name"])
    model = T5ForConditionalGeneration.from_pretrained(CONFIG["model_name"])
    model.to(device)

    train_ds = PromptDataset(train_pairs, tokenizer, CONFIG["max_input_length"], CONFIG["max_output_length"])
    val_ds = PromptDataset(val_pairs, tokenizer, CONFIG["max_input_length"], CONFIG["max_output_length"])

    train_loader = DataLoader(train_ds, batch_size=CONFIG["batch_size"], shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=CONFIG["batch_size"], shuffle=False, num_workers=0)

    total_steps = (len(train_loader) // CONFIG["gradient_accumulation_steps"]) * CONFIG["num_epochs"]
    warmup_steps = int(total_steps * CONFIG["warmup_ratio"])

    optimizer = AdamW(model.parameters(), lr=CONFIG["learning_rate"], weight_decay=0.01)
    scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)

    best_val = float("inf")
    start = time.time()

    print(f"\n{'Epoch':>6}  {'Train Loss':>10}  {'Val Loss':>10}  {'Best':>6}")
    print("-" * 40)

    for epoch in range(1, CONFIG["num_epochs"] + 1):
        t_loss = run_epoch(model, train_loader, optimizer, scheduler, training=True)
        v_loss = run_epoch(model, val_loader, optimizer, scheduler, training=False)

        is_best = v_loss < best_val
        if is_best:
            best_val = v_loss
            model.save_pretrained(CONFIG["output_path"])
            tokenizer.save_pretrained(CONFIG["output_path"])

        marker = " *" if is_best else ""
        print(f"{epoch:>6}  {t_loss:>10.4f}  {v_loss:>10.4f}  {marker}")

        if epoch % CONFIG["save_every_n_epochs"] == 0:
            ckpt = MODELS_DIR / f"checkpoint_epoch_{epoch}"
            model.save_pretrained(ckpt)
            tokenizer.save_pretrained(ckpt)
            print(f"         Checkpoint saved: {ckpt}")

    elapsed = (time.time() - start) / 60
    print(f"\nDone in {elapsed:.1f} min. Best val loss: {best_val:.4f}")
    print(f"Model saved to: {CONFIG['output_path']}")

    # Load best model and show test outputs
    best_model = T5ForConditionalGeneration.from_pretrained(CONFIG["output_path"]).to(device)
    best_tok = T5Tokenizer.from_pretrained(CONFIG["output_path"])
    test_examples(best_model, best_tok)

    # Save training metadata
    info = {
        "model": CONFIG["model_name"],
        "dataset_size": len(train_pairs) + len(val_pairs),
        "train_size": len(train_pairs),
        "val_size": len(val_pairs),
        "epochs": CONFIG["num_epochs"],
        "best_val_loss": best_val,
        "training_minutes": elapsed,
        "device": str(device),
    }
    with open(MODELS_DIR / "training_info.json", "w") as f:
        json.dump(info, f, indent=2)
    print("Training info saved.")


if __name__ == "__main__":
    main()
