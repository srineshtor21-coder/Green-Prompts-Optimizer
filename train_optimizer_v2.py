"""
GreenPromptsOptimizer: Training Script v3 (T5-base, 14k dataset)
Trains T5-base on the expanded dataset for best optimization quality.

Usage:
    python train_optimizer_v3.py

Output:
    models/prompt_optimizer/   <-- upload this folder to Hugging Face
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
    # T5-base is 4x more capable than T5-small and fixes most accuracy issues.
    # Change back to "t5-small" only if your machine runs out of RAM.
    "model_name": "t5-base",

    "dataset_path": "data/training_dataset_10k.json",
    "output_path": "models/prompt_optimizer",

    # Larger batch = more stable gradients with a big dataset.
    "batch_size": 16,

    # With 14k pairs, fewer epochs are needed to avoid overfitting.
    "num_epochs": 15,

    # Lower LR is better for larger models.
    "learning_rate": 1e-4,

    # Shorter sequences = faster training, outputs are short phrases anyway.
    "max_input_length": 128,
    "max_output_length": 32,

    "warmup_ratio": 0.05,
    "gradient_accumulation_steps": 2,

    # Fraction of data held out for validation.
    "val_split": 0.1,

    # Save a checkpoint every N epochs (in addition to best-model saves).
    "save_every_n_epochs": 5,

    # Stop early if validation loss does not improve for this many epochs.
    "early_stopping_patience": 4,
}

DATA_DIR = Path("data")
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")
if device.type == "cpu":
    print("Note: training on CPU. T5-base will take roughly 2-3 hours.")
    print("      If you have a GPU available, set CUDA_VISIBLE_DEVICES=0.")


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
    with open(CONFIG["dataset_path"], encoding="utf-8") as f:
        raw = json.load(f)
    pairs = raw["data"]
    np.random.seed(42)
    np.random.shuffle(pairs)
    n_val = int(len(pairs) * CONFIG["val_split"])
    train, val = pairs[n_val:], pairs[:n_val]
    print(f"Dataset loaded: {len(train)} train, {len(val)} val")
    return train, val


def run_epoch(model, loader, optimizer, scheduler, training=True):
    model.train() if training else model.eval()
    total_loss = 0.0
    steps = 0

    with (torch.enable_grad() if training else torch.no_grad()):
        for step, batch in enumerate(loader):
            ids   = batch["input_ids"].to(device)
            mask  = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            out  = model(input_ids=ids, attention_mask=mask, labels=labels)
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
    """Run a few sample prompts and print before/after."""
    model.eval()
    examples = [
        "Can you please help me understand how neural networks work in a very detailed way?",
        "I'm struggling to figure out how to reverse a linked list in Python could you help me",
        "What is machine learning?",
        "I would really like to know about quantum computing and how it differs from classical computing",
        "Could you kindly explain the process of photosynthesis and why it matters for life on earth?",
        "How do I sort a list in Python?",
        "I need you to very thoroughly explain what Docker containers are and how they work in practice",
        "Can you please tell me about the causes and major effects of World War II?",
        "I want to really understand how to implement a binary search tree from scratch in Python",
        "Hey could you explain what carbon capture technology is and how it works to reduce emissions?",
    ]
    print("\n--- Sample outputs (input -> optimized) ---")
    for prompt in examples:
        ids = tokenizer.encode(
            f"optimize: {prompt}",
            return_tensors="pt",
            max_length=CONFIG["max_input_length"],
            truncation=True,
        ).to(device)
        with torch.no_grad():
            out = model.generate(
                ids,
                max_length=CONFIG["max_output_length"],
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=2,
            )
        result = tokenizer.decode(out[0], skip_special_tokens=True)
        in_words  = len(prompt.split())
        out_words = len(result.split())
        reduction = 100 * (1 - out_words / max(in_words, 1))
        print(f"  IN  ({in_words:>3}w): {prompt[:70]}")
        print(f"  OUT ({out_words:>3}w): {result}   [{reduction:.0f}% shorter]")
        print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 65)
    print("GreenPromptsOptimizer: Training v3")
    print(f"Model: {CONFIG['model_name']}  |  Device: {device}")
    print("=" * 65)

    train_pairs, val_pairs = load_data()

    tokenizer = T5Tokenizer.from_pretrained(CONFIG["model_name"])
    model     = T5ForConditionalGeneration.from_pretrained(CONFIG["model_name"])
    model.to(device)

    train_ds = PromptDataset(train_pairs, tokenizer, CONFIG["max_input_length"], CONFIG["max_output_length"])
    val_ds   = PromptDataset(val_pairs,   tokenizer, CONFIG["max_input_length"], CONFIG["max_output_length"])

    train_loader = DataLoader(train_ds, batch_size=CONFIG["batch_size"], shuffle=True,  num_workers=0)
    val_loader   = DataLoader(val_ds,   batch_size=CONFIG["batch_size"], shuffle=False, num_workers=0)

    total_steps  = (len(train_loader) // CONFIG["gradient_accumulation_steps"]) * CONFIG["num_epochs"]
    warmup_steps = int(total_steps * CONFIG["warmup_ratio"])

    optimizer = AdamW(model.parameters(), lr=CONFIG["learning_rate"], weight_decay=0.01)
    scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)

    best_val   = float("inf")
    no_improve = 0
    start      = time.time()

    print(f"\n{'Epoch':>6}  {'Train':>8}  {'Val':>8}  {'Best':>6}  {'Time':>6}")
    print("-" * 45)

    for epoch in range(1, CONFIG["num_epochs"] + 1):
        t0 = time.time()
        t_loss = run_epoch(model, train_loader, optimizer, scheduler, training=True)
        v_loss = run_epoch(model, val_loader,   optimizer, scheduler, training=False)
        elapsed = (time.time() - t0) / 60

        is_best = v_loss < best_val
        if is_best:
            best_val   = v_loss
            no_improve = 0
            model.save_pretrained(CONFIG["output_path"])
            tokenizer.save_pretrained(CONFIG["output_path"])
            marker = " *"
        else:
            no_improve += 1
            marker = ""

        print(f"{epoch:>6}  {t_loss:>8.4f}  {v_loss:>8.4f}  {best_val:>6.4f}  {elapsed:>4.1f}m{marker}")

        if epoch % CONFIG["save_every_n_epochs"] == 0:
            ckpt = MODELS_DIR / f"checkpoint_epoch_{epoch}"
            model.save_pretrained(ckpt)
            tokenizer.save_pretrained(ckpt)
            print(f"         Checkpoint: {ckpt}")

        if no_improve >= CONFIG["early_stopping_patience"]:
            print(f"\nEarly stopping: no improvement for {no_improve} epochs.")
            break

    elapsed_total = (time.time() - start) / 60
    print(f"\nDone in {elapsed_total:.1f} min. Best val loss: {best_val:.4f}")
    print(f"Best model saved to: {CONFIG['output_path']}")

    # Load best model and show sample outputs
    best_model = T5ForConditionalGeneration.from_pretrained(CONFIG["output_path"]).to(device)
    best_tok   = T5Tokenizer.from_pretrained(CONFIG["output_path"])
    test_examples(best_model, best_tok)

    # Save metadata
    info = {
        "model":         CONFIG["model_name"],
        "dataset_size":  len(train_pairs) + len(val_pairs),
        "train_size":    len(train_pairs),
        "val_size":      len(val_pairs),
        "epochs_run":    epoch,
        "best_val_loss": best_val,
        "training_min":  elapsed_total,
        "device":        str(device),
    }
    with open(MODELS_DIR / "training_info.json", "w") as f:
        json.dump(info, f, indent=2)
    print("Training info saved.")


if __name__ == "__main__":
    main()
