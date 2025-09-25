import os
import random
import numpy as np

from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# ------------------------------------------------------------
# 1. Load Dataset
# ------------------------------------------------------------
DATASET_HUB_PATH = "Cesarj66/quote-category-detection"
dataset = load_dataset(DATASET_HUB_PATH)

# ------------------------------------------------------------
# 2. Label Encoding
# ------------------------------------------------------------
label_names = ["Statement", "Imperative", "Question", "Analogy/Metaphor", "Justification", "Warning", "Encouragement", "NoCategory"]
label2id = {label: i for i, label in enumerate(label_names)}
id2label = {i: label for label, i in label2id.items()}

def encode_labels(example):
    example["label"] = label2id.get(example["label"], label2id["NoCategory"])
    return example

# ------------------------------------------------------------
# 3. Tokenizer & Preprocessing
# ------------------------------------------------------------
MODEL_NAME = "roberta-large"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def preprocess_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=64)

# Apply preprocessing and label encoding
tokenized_train = dataset["train"].map(preprocess_function, batched=True).map(encode_labels)
tokenized_val = dataset["validation"].map(preprocess_function, batched=True).map(encode_labels)
tokenized_test = dataset["test"].map(preprocess_function, batched=True).map(encode_labels)

# ------------------------------------------------------------
# 4. Load the Pretrained Model for Classification
# ------------------------------------------------------------
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(label_names),
    id2label=id2label,
    label2id=label2id
)

# ------------------------------------------------------------
# 5. Define the Metrics Function
# ------------------------------------------------------------
def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    preds = np.argmax(predictions, axis=1)

    acc = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="macro")
    return {
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

# ------------------------------------------------------------
# 6. Training Arguments
# ------------------------------------------------------------
training_args = TrainingArguments(
    output_dir="training_output",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=8,
    warmup_steps=0,
    weight_decay=0.01,
    logging_dir="logs",
    logging_steps=50,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,
    push_to_hub=True,
    hub_model_id="Cesarj66/cat-detection-roberta-large",
    hub_strategy="end"
)

# ------------------------------------------------------------
# 7. Trainer
# ------------------------------------------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    compute_metrics=compute_metrics
)

# ------------------------------------------------------------
# 8. Train and Evaluate
# ------------------------------------------------------------
trainer.train()

val_metrics = trainer.evaluate()
print("Validation metrics:", val_metrics)

test_metrics = trainer.evaluate(tokenized_test)
print("Test metrics:", test_metrics)

# ------------------------------------------------------------
# 9. Push model and tokenizer to Hugging Face Hub
# ------------------------------------------------------------
model.push_to_hub("Cesarj66/cat-detection-roberta-large")
tokenizer.push_to_hub("Cesarj66/cat-detection-roberta-large")
print("Model and tokenizer pushed to Hugging Face Hub!")
