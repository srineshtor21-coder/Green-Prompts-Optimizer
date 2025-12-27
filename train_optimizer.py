"""
GreenPrompts Model Trainer
Trains T5 model to optimize verbose prompts
"""

import torch
from transformers import (
    T5Tokenizer, 
    T5ForConditionalGeneration,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq
)
from datasets import Dataset
import json
import os


def load_training_data(filename="prompt_dataset.json"):
    """Load training data from JSON file"""
    print(f"📂 Loading training data from {filename}...")
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Dataset file not found: {filename}")
    
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data)} training pairs")
    return data


def prepare_dataset(data, tokenizer, max_input_length=128, max_target_length=64):
    """Prepare dataset for training"""
    print("🔧 Preparing dataset...")
    
    inputs = [f"optimize: {item['verbose']}" for item in data]
    targets = [item['optimized'] for item in data]
    
    model_inputs = tokenizer(
        inputs,
        max_length=max_input_length,
        truncation=True,
        padding='max_length'
    )
    
    labels = tokenizer(
        targets,
        max_length=max_target_length,
        truncation=True,
        padding='max_length'
    )
    
    labels['input_ids'] = [
        [(l if l != tokenizer.pad_token_id else -100) for l in label]
        for label in labels['input_ids']
    ]
    
    model_inputs['labels'] = labels['input_ids']
    
    dataset = Dataset.from_dict({
        'input_ids': model_inputs['input_ids'],
        'attention_mask': model_inputs['attention_mask'],
        'labels': model_inputs['labels']
    })
    
    print(f"✅ Dataset prepared: {len(dataset)} examples")
    return dataset


def train_model(
    model_name="t5-small",
    output_dir="optimizer_model",
    num_epochs=10,
    batch_size=8
):
    """Train the prompt optimizer model"""
    
    print("\n" + "="*70)
    print("🌱 GreenPrompts Model Training")
    print("="*70)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"💻 Device: {device}\n")
    
    print(f"📥 Loading {model_name}...")
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    print("✅ Model loaded\n")
    
    training_data = load_training_data()
    dataset = prepare_dataset(training_data, tokenizer)
    
    split_dataset = dataset.train_test_split(test_size=0.1, seed=42)
    train_dataset = split_dataset['train']
    eval_dataset = split_dataset['test']
    
    print(f"📊 Training samples: {len(train_dataset)}")
    print(f"📊 Validation samples: {len(eval_dataset)}\n")
    
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model
    )
    
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir=f"{output_dir}/logs",
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        learning_rate=5e-5,
        save_total_limit=2,
        report_to="none",
        push_to_hub=False
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer
    )
    
    print("🚀 Starting training...\n")
    trainer.train()
    
    print("\n✅ Training completed!")
    print(f"💾 Saving model to {output_dir}...")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("✅ Model saved!\n")


if __name__ == "__main__":
    if not os.path.exists("prompt_dataset.json"):
        print("❌ Error: prompt_dataset.json not found!")
        print("Please run build_dataset.py first.")
        exit(1)
    
    train_model()
