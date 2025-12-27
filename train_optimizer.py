"""
Green-Prompts-Optimizer: Model Training Script
Trains T5 model on 127 prompt optimization pairs
"""

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import T5Tokenizer, T5ForConditionalGeneration, AdamW
from transformers import get_linear_schedule_with_warmup
import json
from pathlib import Path
import time
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    'model_name': 't5-small',
    'batch_size': 4,
    'num_epochs': 30,
    'learning_rate': 3e-4,
    'max_input_length': 256,
    'max_output_length': 128,
    'warmup_steps': 100,
    'gradient_accumulation_steps': 4,
    'save_steps': 50,
    'eval_steps': 25
}

# Paths
DATA_DIR = Path("data")
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

DATASET_PATH = DATA_DIR / "training_dataset.json"
MODEL_SAVE_PATH = MODELS_DIR / "prompt_optimizer"

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# ============================================================================
# DATASET CLASS
# ============================================================================

class PromptOptimizationDataset(Dataset):
    """Custom dataset for prompt optimization"""
    
    def __init__(self, data, tokenizer, max_input_length, max_output_length):
        self.data = data
        self.tokenizer = tokenizer
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # Prepare input with task prefix
        input_text = f"optimize: {item['original']}"
        target_text = item['optimized']
        
        # Tokenize input
        input_encoding = self.tokenizer(
            input_text,
            max_length=self.max_input_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Tokenize target
        target_encoding = self.tokenizer(
            target_text,
            max_length=self.max_output_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        labels = target_encoding['input_ids']
        labels[labels == self.tokenizer.pad_token_id] = -100
        
        return {
            'input_ids': input_encoding['input_ids'].flatten(),
            'attention_mask': input_encoding['attention_mask'].flatten(),
            'labels': labels.flatten()
        }

# ============================================================================
# TRAINING FUNCTIONS
# ============================================================================

def load_dataset():
    """Load the training dataset"""
    print("Loading dataset...")
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        dataset_json = json.load(f)
    
    data = dataset_json['data']
    print(f"✓ Loaded {len(data)} training examples")
    
    return data

def split_dataset(data, train_ratio=0.85):
    """Split dataset into train and validation sets"""
    np.random.shuffle(data)
    split_idx = int(len(data) * train_ratio)
    
    train_data = data[:split_idx]
    val_data = data[split_idx:]
    
    print(f"✓ Train set: {len(train_data)} examples")
    print(f"✓ Validation set: {len(val_data)} examples")
    
    return train_data, val_data

def train_epoch(model, dataloader, optimizer, scheduler, device, epoch, total_epochs):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    progress_bar = tqdm(dataloader, desc=f"Epoch {epoch}/{total_epochs}")
    
    for step, batch in enumerate(progress_bar):
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
        
        loss = outputs.loss
        total_loss += loss.item()
        
        # Backward pass
        loss = loss / CONFIG['gradient_accumulation_steps']
        loss.backward()
        
        if (step + 1) % CONFIG['gradient_accumulation_steps'] == 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
        
        # Update progress bar
        avg_loss = total_loss / (step + 1)
        progress_bar.set_postfix({'loss': f'{avg_loss:.4f}'})
    
    return total_loss / len(dataloader)

def evaluate(model, dataloader, device):
    """Evaluate the model"""
    model.eval()
    total_loss = 0
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            total_loss += outputs.loss.item()
    
    return total_loss / len(dataloader)

def test_model(model, tokenizer, device, test_prompts):
    """Test the model on example prompts"""
    model.eval()
    print("\n" + "=" * 70)
    print("TESTING MODEL ON EXAMPLE PROMPTS")
    print("=" * 70)
    
    for prompt in test_prompts:
        input_text = f"optimize: {prompt}"
        input_ids = tokenizer.encode(input_text, return_tensors='pt').to(device)
        
        with torch.no_grad():
            outputs = model.generate(
                input_ids,
                max_length=128,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=2
            )
        
        optimized = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        print(f"\nOriginal: {prompt}")
        print(f"Optimized: {optimized}")
        print(f"Reduction: {len(prompt)} → {len(optimized)} chars "
              f"({100 * (1 - len(optimized)/len(prompt)):.1f}%)")

def plot_training_history(train_losses, val_losses):
    """Plot training and validation loss"""
    plt.figure(figsize=(10, 6))
    plt.plot(train_losses, label='Training Loss', linewidth=2)
    plt.plot(val_losses, label='Validation Loss', linewidth=2)
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.title('Training History - Green Prompts Optimizer', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plot_path = MODELS_DIR / 'training_history.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Training plot saved to {plot_path}")

# ============================================================================
# MAIN TRAINING SCRIPT
# ============================================================================

def main():
    """Main training function"""
    print("=" * 70)
    print("GREEN-PROMPTS-OPTIMIZER: MODEL TRAINING")
    print("=" * 70)
    print(f"Model: {CONFIG['model_name']}")
    print(f"Device: {device}")
    print(f"Batch size: {CONFIG['batch_size']}")
    print(f"Epochs: {CONFIG['num_epochs']}")
    print(f"Learning rate: {CONFIG['learning_rate']}")
    print("=" * 70 + "\n")
    
    # Load dataset
    data = load_dataset()
    train_data, val_data = split_dataset(data)
    
    # Initialize tokenizer and model
    print("\nInitializing model...")
    tokenizer = T5Tokenizer.from_pretrained(CONFIG['model_name'])
    model = T5ForConditionalGeneration.from_pretrained(CONFIG['model_name'])
    model.to(device)
    print("✓ Model initialized\n")
    
    # Create datasets
    train_dataset = PromptOptimizationDataset(
        train_data, tokenizer, 
        CONFIG['max_input_length'], 
        CONFIG['max_output_length']
    )
    
    val_dataset = PromptOptimizationDataset(
        val_data, tokenizer,
        CONFIG['max_input_length'],
        CONFIG['max_output_length']
    )
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=CONFIG['batch_size'],
        shuffle=True,
        num_workers=0
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=CONFIG['batch_size'],
        shuffle=False,
        num_workers=0
    )
    
    # Initialize optimizer and scheduler
    optimizer = AdamW(model.parameters(), lr=CONFIG['learning_rate'])
    
    total_steps = len(train_loader) * CONFIG['num_epochs']
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=CONFIG['warmup_steps'],
        num_training_steps=total_steps
    )
    
    # Training loop
    print("Starting training...\n")
    train_losses = []
    val_losses = []
    best_val_loss = float('inf')
    start_time = time.time()
    
    for epoch in range(1, CONFIG['num_epochs'] + 1):
        print(f"\n{'='*70}")
        print(f"EPOCH {epoch}/{CONFIG['num_epochs']}")
        print(f"{'='*70}")
        
        # Train
        train_loss = train_epoch(
            model, train_loader, optimizer, scheduler, 
            device, epoch, CONFIG['num_epochs']
        )
        train_losses.append(train_loss)
        
        # Validate
        val_loss = evaluate(model, val_loader, device)
        val_losses.append(val_loss)
        
        print(f"\nEpoch {epoch} Results:")
        print(f"  Train Loss: {train_loss:.4f}")
        print(f"  Val Loss: {val_loss:.4f}")
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            print(f"  ✓ New best model! Saving...")
            model.save_pretrained(MODEL_SAVE_PATH)
            tokenizer.save_pretrained(MODEL_SAVE_PATH)
        
        # Save checkpoint
        if epoch % 5 == 0:
            checkpoint_path = MODELS_DIR / f"checkpoint_epoch_{epoch}"
            model.save_pretrained(checkpoint_path)
            tokenizer.save_pretrained(checkpoint_path)
            print(f"  ✓ Checkpoint saved to {checkpoint_path}")
    
    # Training complete
    training_time = time.time() - start_time
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE!")
    print("=" * 70)
    print(f"Total training time: {training_time/60:.2f} minutes")
    print(f"Best validation loss: {best_val_loss:.4f}")
    print(f"Final model saved to: {MODEL_SAVE_PATH}")
    
    # Plot training history
    plot_training_history(train_losses, val_losses)
    
    # Test the model
    test_prompts = [
        "Can you please help me write a Python function that takes a list of numbers and returns the sum?",
        "I need to understand how machine learning works and what are the main algorithms",
        "What are some good strategies for improving my productivity at work?",
        "Could you explain to me how to create a website using HTML and CSS?",
        "I'm trying to learn about climate change and its effects on the environment"
    ]
    
    test_model(model, tokenizer, device, test_prompts)
    
    # Save training info
    training_info = {
        'config': CONFIG,
        'dataset_size': len(data),
        'train_size': len(train_data),
        'val_size': len(val_data),
        'num_epochs': CONFIG['num_epochs'],
        'best_val_loss': best_val_loss,
        'final_train_loss': train_losses[-1],
        'training_time_minutes': training_time / 60,
        'device': str(device)
    }
    
    with open(MODELS_DIR / 'training_info.json', 'w') as f:
        json.dump(training_info, f, indent=2)
    
    print("\n✓ Training information saved")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
